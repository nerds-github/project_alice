import React, { createContext, useContext, ReactNode, useCallback } from 'react';
import {
    fetchItem as apiFetchItem,
    createItem as apiCreateItem,
    updateItem as apiUpdateItem,
    executeTask as apiExecuteTask,
    generateChatResponse as apiGenerateChatResponse,
    sendMessage as apiSendMessage,
    purgeAndReinitializeDatabase as apiPurgeAndReinitializeDatabase,
    uploadFileContentReference as apiUploadFileContentReference,
    updateFile as apiUpdateFile,
    retrieveFile as apiRetrieveFile,
    requestFileTranscript as apiRequestFileTranscript,
    updateMessageInChat as apiUpdateMessageInChat,
    deleteItem as apiDeleteItem
} from '../services/api';
import { useNotification } from './NotificationContext';
import { useCardDialog } from './CardDialogContext';
import { CollectionName, CollectionType, CollectionElementString, collectionNameToElementString } from '../types/CollectionTypes';
import { AliceChat } from '../types/ChatTypes';
import { MessageType } from '../types/MessageTypes';
import { TaskResponse } from '../types/TaskResponseTypes';
import { FileReference, FileContentReference } from '../types/FileTypes';
import { useDialog } from './DialogCustomContext';
import Logger from '../utils/Logger';
import { globalEventEmitter } from '../utils/EventEmitter';

interface ApiContextType {
    fetchItem: typeof apiFetchItem;
    createItem: typeof apiCreateItem;
    updateItem: typeof apiUpdateItem;
    executeTask: typeof apiExecuteTask;
    generateChatResponse: typeof apiGenerateChatResponse;
    sendMessage: typeof apiSendMessage;
    purgeAndReinitializeDatabase: typeof apiPurgeAndReinitializeDatabase;
    uploadFileContentReference: typeof apiUploadFileContentReference;
    updateFile: typeof apiUpdateFile;
    retrieveFile: typeof apiRetrieveFile;
    requestFileTranscript: typeof apiRequestFileTranscript;
    updateMessageInChat: typeof apiUpdateMessageInChat;
    deleteItem: <T extends CollectionName>(collectionName: T, itemId: string) => Promise<boolean>;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

export const useApi = () => {
    const context = useContext(ApiContext);
    if (context === undefined) {
        throw new Error('useApi must be used within an ApiProvider');
    }
    return context;
};

export const ApiProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const { addNotification } = useNotification();
    const { selectCardItem } = useCardDialog();
    const { openDialog } = useDialog();

    const emitEvent = (eventType: string, collectionName: CollectionName, item: any) => {
        globalEventEmitter.emit(`${eventType}:${collectionName}`, item);
    };

    const createItem = useCallback(async <T extends CollectionName>(
        collectionName: T,
        itemData: Partial<CollectionType[T]>
    ): Promise<CollectionType[T]> => {
        try {
            const createdItem = await apiCreateItem(collectionName, itemData);
            Logger.debug(`Created ${collectionName}:`, createdItem);
            addNotification(
                `${collectionName} created successfully`,
                'success',
                5000,
                {
                    label: 'View',
                    onClick: () => selectCardItem(collectionNameToElementString[collectionName] as CollectionElementString, createdItem._id as string)
                }
            );
            emitEvent('created', collectionName, createdItem);
            return createdItem;
        } catch (error) {
            addNotification(`Error creating ${collectionName}`, 'error');
            throw error;
        }
    }, [addNotification, selectCardItem]);

    const updateItem = useCallback(async <T extends CollectionName>(
        collectionName: T,
        itemId: string,
        itemData: Partial<CollectionType[T]>
    ): Promise<CollectionType[T]> => {
        try {
            const updatedItem = await apiUpdateItem(collectionName, itemId, itemData);
            addNotification(
                `${collectionName} updated successfully`,
                'success',
                5000,
                {
                    label: 'View',
                    onClick: () => selectCardItem(collectionNameToElementString[collectionName] as CollectionElementString, itemId)
                }
            );
            emitEvent('updated', collectionName, updatedItem);
            return updatedItem;
        } catch (error) {
            addNotification(`Error updating ${collectionName}`, 'error');
            throw error;
        }
    }, [addNotification, selectCardItem]);

    const deleteItem = useCallback(async <T extends CollectionName>(
        collectionName: T,
        itemId: string
    ): Promise<boolean> => {
        return new Promise((resolve) => {
            openDialog({
                title: 'Confirm Deletion',
                content: `Are you sure you want to delete this ${collectionNameToElementString[collectionName]}?`,
                confirmText: 'Delete',
                cancelText: 'Cancel',
                onConfirm: async () => {
                    try {
                        await apiDeleteItem(collectionName, itemId);
                        addNotification(`${collectionNameToElementString[collectionName]} deleted successfully`, 'success');
                        emitEvent('deleted', collectionName, { _id: itemId });
                        resolve(true);
                    } catch (error) {
                        addNotification(`Error deleting ${collectionName}`, 'error');
                        Logger.error(`Error deleting item from ${collectionName}:`, error);
                        resolve(false);
                    }
                },
                onCancel: () => {
                    addNotification(`Deletion of ${collectionName} cancelled`, 'info');
                    resolve(false);
                }
            });
        });
    }, [addNotification, openDialog]);

    const executeTask = useCallback(async (taskId: string, inputs: any): Promise<TaskResponse> => {
        try {
            const result = await apiExecuteTask(taskId, inputs);
            addNotification('Task executed successfully', 'success', 5000, {
                label: 'View Result',
                onClick: () => selectCardItem('TaskResponse', result._id as string)
            });
            emitEvent('created', 'taskresults', result);
            return result;
        } catch (error) {
            addNotification('Error executing task', 'error');
            throw error;
        }
    }, [addNotification, selectCardItem]);

    const generateChatResponse = useCallback(async (chatId: string): Promise<boolean> => {
        try {
            const result = await apiGenerateChatResponse(chatId);
            addNotification('Chat response generated successfully', 'success');
            if (result) {
                const updatedChat = await apiFetchItem('chats', chatId) as AliceChat;
                emitEvent('updated', 'chats', updatedChat);
            }
            return result;
        } catch (error) {
            addNotification('Error generating chat response', 'error');
            throw error;
        }
    }, [addNotification]);

    const sendMessage = useCallback(async (chatId: string, message: MessageType): Promise<AliceChat> => {
        try {
            const result = await apiSendMessage(chatId, message);
            addNotification('Message sent successfully', 'success');
            emitEvent('created', 'messages', message);
            emitEvent('updated', 'chats', result);
            return result;
        } catch (error) {
            addNotification('Error sending message', 'error');
            throw error;
        }
    }, [addNotification]);

    const uploadFileContentReference = useCallback(async (itemData: Partial<FileContentReference>): Promise<FileReference> => {
        try {
            const result = await apiUploadFileContentReference(itemData);
            addNotification('File uploaded successfully', 'success', 5000, {
                label: 'View File',
                onClick: () => selectCardItem('File', result._id as string)
            });
            emitEvent('created', 'files', result);
            return result;
        } catch (error) {
            addNotification('Error uploading file', 'error');
            throw error;
        }
    }, [addNotification, selectCardItem]);

    const updateFile = useCallback(async (file: File, fileId?: string): Promise<FileReference> => {
        try {
            const result = await apiUpdateFile(file, fileId);
            addNotification('File updated successfully', 'success', 5000, {
                label: 'View File',
                onClick: () => selectCardItem('File', result._id as string, result)
            });
            emitEvent('updated', 'files', result);
            return result;
        } catch (error) {
            addNotification('Error updating file', 'error');
            throw error;
        }
    }, [addNotification, selectCardItem]);

    const requestFileTranscript = useCallback(async (fileId: string, agentId?: string, chatId?: string): Promise<MessageType> => {
        try {
            Logger.info(`Requesting transcript for file: ${fileId}`);
            const fileData = await apiFetchItem('files', fileId) as FileReference;

            if (fileData.transcript) {
                return new Promise((resolve, reject) => {
                    openDialog({
                        title: 'Existing Transcript',
                        content: 'This file already has a transcript. Do you want to generate a new one?',
                        confirmText: 'Generate New',
                        cancelText: 'Use Existing',
                        onConfirm: async () => {
                            try {
                                const newTranscript = await apiRequestFileTranscript(fileId, agentId, chatId);
                                await updateItem('files', fileId, { transcript: newTranscript });
                                addNotification('New transcript generated successfully', 'success');
                                resolve(newTranscript);
                            } catch (error) {
                                addNotification('Error generating new transcript', 'error');
                                reject(error);
                            }
                        },
                        onCancel: () => {
                            addNotification('Using existing transcript', 'info');
                            resolve(fileData.transcript as MessageType);
                        }
                    });
                });
            } else {
                const transcript = await apiRequestFileTranscript(fileId, agentId, chatId);
                await updateItem('files', fileId, { transcript: transcript });
                addNotification('Transcript generated successfully', 'success');
                return transcript;
            }
        } catch (error) {
            addNotification('Error requesting transcript', 'error');
            throw error;
        }
    }, [addNotification, openDialog, updateItem]);

    const updateMessageInChat = useCallback(async (chatId: string, message: MessageType): Promise<MessageType> => {
        try {
            const result = await apiUpdateMessageInChat(chatId, message);
            addNotification('Message updated successfully', 'success');
            emitEvent('updated', 'messages', result);
            const updatedChat = await apiFetchItem('chats', chatId) as AliceChat;
            emitEvent('updated', 'chats', updatedChat);
            return result;
        } catch (error) {
            addNotification('Error updating message', 'error');
            throw error;
        }
    }, [addNotification]);
    const purgeAndReinitializeDatabase = useCallback(async (): Promise<void> => {
        try {
            await apiPurgeAndReinitializeDatabase();
            addNotification('Database purged and reinitialized successfully', 'success');
            globalEventEmitter.emit('databasePurged');
        } catch (error) {
            addNotification('Error purging and reinitializing database', 'error');
            Logger.error('Error purging and reinitializing database:', error);
            throw error;
        }
    }, [addNotification]);

    const value: ApiContextType = {
        fetchItem: apiFetchItem,
        createItem,
        updateItem,
        deleteItem,
        executeTask,
        generateChatResponse,
        sendMessage,
        purgeAndReinitializeDatabase,
        uploadFileContentReference,
        updateFile,
        retrieveFile: apiRetrieveFile,
        requestFileTranscript,
        updateMessageInChat
    };

    return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};