/**
 * Debts page - Manage debts: add manual, upload OCR, edit, delete
 * Design aligned with landing page styling
 */

import { useEffect, useState } from 'react';
import { Plus, Upload as UploadIcon } from 'lucide-react';
import { DebtList } from '../components/debt/DebtList';
import { DebtForm } from '../components/debt/DebtForm';
import type { DebtFormData } from '../components/debt/DebtForm';
import { FileDropzone } from '../components/upload/FileDropzone';
import { OCRFeedback } from '../components/upload/OCRFeedback';
import { Modal } from '../components/common/Modal';
import { Button } from '../components/common/Button';
import { useDebts } from '../hooks/useDebts';
import uploadService from '../services/uploadService';
import type { ExtractedDebt } from '../services/uploadService';
import type { Debt } from '../stores/debtStore';

type UploadStatus = 'idle' | 'processing' | 'completed' | 'failed';

export default function Debts() {
    const {
        debts,
        summary,
        loading,
        fetchDebts,
        createDebt,
        editDebt,
        deleteDebt,
        markPaidOff,
    } = useDebts();

    // Modal states
    const [showAddModal, setShowAddModal] = useState(false);
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [editingDebt, setEditingDebt] = useState<Debt | null>(null);
    const [deletingDebt, setDeletingDebt] = useState<Debt | null>(null);

    // Upload states
    const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
    const [uploadProgress, setUploadProgress] = useState(0);
    const [extractedDebts, setExtractedDebts] = useState<ExtractedDebt[]>([]);
    const [uploadError, setUploadError] = useState<string | null>(null);

    useEffect(() => {
        fetchDebts();
    }, [fetchDebts]);

    const handleAddDebt = async (data: DebtFormData) => {
        try {
            await createDebt(data);
            setShowAddModal(false);
        } catch (err: any) {
            alert(err.message || 'Failed to add debt');
        }
    };

    const handleEditDebt = async (data: DebtFormData) => {
        if (editingDebt) {
            await editDebt(editingDebt.id, data);
            setEditingDebt(null);
        }
    };

    const handleDeleteDebt = async () => {
        if (deletingDebt) {
            await deleteDebt(deletingDebt.id);
            setDeletingDebt(null);
        }
    };

    const handleMarkPaidOff = async (debt: Debt) => {
        if (confirm(`Mark "${debt.creditor_name}" as paid off?`)) {
            await markPaidOff(debt.id);
        }
    };

    const handleFileUpload = async (file: File) => {
        setUploadStatus('processing');
        setUploadProgress(10);
        setUploadError(null);
        setExtractedDebts([]);

        try {
            // Upload the file
            const uploadResponse = await uploadService.uploadDocument(file, 'other');
            setUploadProgress(30);

            // Poll for completion
            const result = await uploadService.waitForCompletion(
                uploadResponse.id,
                (status) => {
                    setUploadProgress(30 + status.progress_percentage * 0.6);
                }
            );

            if (result.status === 'completed' && result.result) {
                setExtractedDebts(result.result.extracted_debts);
                setUploadStatus('completed');
                setUploadProgress(100);
            } else {
                setUploadStatus('failed');
                setUploadError(result.error_message || 'Failed to process document');
            }
        } catch (err: any) {
            setUploadStatus('failed');
            setUploadError(err.message || 'Failed to upload document');
        }
    };

    const handleAddExtractedDebt = async (debt: ExtractedDebt) => {
        const formData: DebtFormData = {
            creditor_name: debt.creditor_name,
            debt_type: debt.debt_type as DebtFormData['debt_type'],
            balance: debt.balance,
            apr: debt.apr || 0,
            minimum_payment: debt.minimum_payment || 0,
            account_number_last4: debt.account_number_last4,
            due_date: debt.due_date,
        };
        await createDebt(formData);
    };

    const handleAddAllExtracted = async (debts: ExtractedDebt[]) => {
        for (const debt of debts) {
            await handleAddExtractedDebt(debt);
        }
    };

    const resetUpload = () => {
        setUploadStatus('idle');
        setUploadProgress(0);
        setExtractedDebts([]);
        setUploadError(null);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">My Debts</h1>
                    <p className="text-slate-500">Track and manage all your debts in one place</p>
                </div>
                <div className="flex gap-3">
                    <Button
                        variant="outline"
                        onClick={() => setShowUploadModal(true)}
                        leftIcon={<UploadIcon className="h-4 w-4" />}
                    >
                        Scan Statement
                    </Button>
                    <Button
                        onClick={() => setShowAddModal(true)}
                        leftIcon={<Plus className="h-4 w-4" />}
                    >
                        Add Debt
                    </Button>
                </div>
            </div>

            {/* Debt List */}
            <DebtList
                debts={debts}
                summary={summary}
                loading={loading}
                onAddDebt={() => setShowAddModal(true)}
                onEditDebt={setEditingDebt}
                onDeleteDebt={setDeletingDebt}
                onMarkPaidOff={handleMarkPaidOff}
            />

            {/* Add Debt Modal */}
            <Modal
                isOpen={showAddModal}
                onClose={() => setShowAddModal(false)}
                title="Add New Debt"
                size="lg"
            >
                <DebtForm
                    onSubmit={handleAddDebt}
                    onCancel={() => setShowAddModal(false)}
                />
            </Modal>

            {/* Edit Debt Modal */}
            <Modal
                isOpen={!!editingDebt}
                onClose={() => setEditingDebt(null)}
                title="Edit Debt"
                size="lg"
            >
                {editingDebt && (
                    <DebtForm
                        initialData={{
                            creditor_name: editingDebt.creditor_name,
                            debt_type: editingDebt.debt_type,
                            // Note: In real app, decrypt these values
                            balance: 0,
                            apr: 0,
                            minimum_payment: 0,
                            account_number_last4: editingDebt.account_number_last4,
                            due_date: editingDebt.due_date,
                            notes: editingDebt.notes,
                        }}
                        onSubmit={handleEditDebt}
                        onCancel={() => setEditingDebt(null)}
                        isEditing
                    />
                )}
            </Modal>

            {/* Delete Confirmation Modal */}
            <Modal
                isOpen={!!deletingDebt}
                onClose={() => setDeletingDebt(null)}
                title="Delete Debt"
                size="sm"
                footer={
                    <div className="flex justify-end gap-3">
                        <Button variant="outline" onClick={() => setDeletingDebt(null)}>
                            Cancel
                        </Button>
                        <Button variant="danger" onClick={handleDeleteDebt}>
                            Delete
                        </Button>
                    </div>
                }
            >
                <p className="text-slate-600">
                    Are you sure you want to delete <strong>{deletingDebt?.creditor_name}</strong>?
                    This action cannot be undone.
                </p>
            </Modal>

            {/* Upload Modal */}
            <Modal
                isOpen={showUploadModal}
                onClose={() => {
                    setShowUploadModal(false);
                    resetUpload();
                }}
                title="Scan Statement"
                size="lg"
            >
                <div className="space-y-6">
                    {uploadStatus === 'idle' && (
                        <>
                            <p className="text-slate-500">
                                Upload a bank or credit card statement image. Our AI will automatically extract debt information.
                            </p>
                            <FileDropzone
                                onFileSelect={handleFileUpload}
                                isUploading={false}
                            />
                        </>
                    )}

                    {uploadStatus !== 'idle' && (
                        <OCRFeedback
                            status={uploadStatus}
                            progress={uploadProgress}
                            extractedDebts={extractedDebts}
                            errorMessage={uploadError || undefined}
                            onAddDebt={handleAddExtractedDebt}
                            onAddAll={handleAddAllExtracted}
                        />
                    )}

                    {uploadStatus === 'completed' && extractedDebts.length > 0 && (
                        <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
                            <Button variant="outline" onClick={resetUpload}>
                                Upload Another
                            </Button>
                            <Button onClick={() => {
                                setShowUploadModal(false);
                                resetUpload();
                            }}>
                                Done
                            </Button>
                        </div>
                    )}

                    {(uploadStatus === 'failed' || (uploadStatus === 'completed' && extractedDebts.length === 0)) && (
                        <div className="flex justify-end pt-4">
                            <Button variant="outline" onClick={resetUpload}>
                                Try Again
                            </Button>
                        </div>
                    )}
                </div>
            </Modal>
        </div>
    );
}
