import React, { useState, useEffect } from 'react';
import './FileList.css';

function FileList() {
    const [files, setFiles] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchFiles();
    }, []);

    const fetchFiles = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/files');
            if (!response.ok) {
                throw new Error('Failed to fetch files');
            }
            const data = await response.json();
            setFiles(data.files || []);
        } catch (error) {
            console.error('Error fetching files:', error);
            setError('Error loading files');
        }
    };

    if (error) {
        return <div className="error-message">{error}</div>;
    }

    return (
        <div className="file-list">
            <h2>Uploaded Files</h2>
            {files.length === 0 ? (
                <p>No files uploaded yet</p>
            ) : (
                <ul>
                    {files.map((file, index) => (
                        <li key={index}>
                            <span className="file-name">{file.name}</span>
                            <span className="file-status">{file.status}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default FileList;
