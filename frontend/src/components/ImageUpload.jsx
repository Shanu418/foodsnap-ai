import React, { useState, useRef } from 'react';
import axios from 'axios';

const ImageUpload = ({ onAnalysisComplete, onAnalysisStart, onError, isLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      onError('Please upload an image file (JPG, PNG, etc.)');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      onError('File size must be less than 10MB');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);

    // Upload and analyze
    await analyzeImage(file);
  };

  const analyzeImage = async (file) => {
    onAnalysisStart();

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/analyze-food', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 seconds timeout
      });

      if (response.data.success) {
        onAnalysisComplete(response.data);
      } else {
        onError('Failed to analyze the image. Please try again.');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      if (error.code === 'ECONNABORTED') {
        onError('Request timeout. Please try again.');
      } else if (error.response) {
        onError(error.response.data.detail || 'Server error occurred');
      } else if (error.request) {
        onError('Network error. Please check your connection.');
      } else {
        onError('An unexpected error occurred');
      }
    }
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  const resetUpload = () => {
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full">
      {!preview ? (
        <div
          className={`upload-area relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all
            ${dragActive 
              ? 'border-green-500 bg-green-50' 
              : 'border-gray-300 hover:border-gray-400 bg-gray-50'
            }
            ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={!isLoading ? onButtonClick : undefined}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept="image/*"
            onChange={handleChange}
            disabled={isLoading}
          />
          
          <div className="space-y-4">
            <div className="mx-auto w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center">
              <svg
                className="w-12 h-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            
            <div>
              <p className="text-lg font-medium text-gray-700">
                {dragActive ? 'Drop your image here' : 'Click to upload or drag and drop'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                PNG, JPG, GIF up to 10MB
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="relative">
            <img
              src={preview}
              alt="Food preview"
              className="w-full h-64 object-cover rounded-lg"
            />
            {!isLoading && (
              <button
                onClick={resetUpload}
                className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
          
          {isLoading && (
            <div className="text-center py-4">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
              <p className="mt-2 text-gray-600">Analyzing food image...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
