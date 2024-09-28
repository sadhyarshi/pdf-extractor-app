import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [fileType, setFileType] = useState('json');
  const [extractedData, setExtractedData] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setFileName(selectedFile.name);
  };

  const handleFileTypeChange = (e) => {
    setFileType(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert('Please upload a PDF file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', fileType);

    try {
      const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `output.${fileType}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      setExtractedData(response.data);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert('File upload failed. Please try again.');
    }
  };

  return (
    <div className="App">
      <h1>PDF Extractor</h1>

      <form onSubmit={handleSubmit} className="form-container">
        <div className="form-group">
          <label htmlFor="fileInput">Upload PDF:</label>
          <input
            type="file"
            id="fileInput"
            accept="application/pdf"
            onChange={handleFileChange}
          />
          {fileName && <p className="file-name">File: {fileName}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="fileType">Select Output Type:</label>
          <select id="fileType" value={fileType} onChange={handleFileTypeChange}>
            <option value="json">JSON</option>
            <option value="text">Text</option>
          </select>
        </div>

        <button type="submit" className="submit-btn">Extract Data</button>
      </form>

      {extractedData && (
        <div className="output-container">
          <h2>Extracted Data</h2>
          <pre>{fileType === 'json' ? JSON.stringify(extractedData, null, 2) : extractedData.content}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
