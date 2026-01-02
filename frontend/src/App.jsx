import React, { useState } from 'react';
import ImageUpload from './components/ImageUpload';
import NutritionResults from './components/NutritionResults';
import './App.css';

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalysisComplete = (result) => {
    setAnalysisResult(result);
    setIsLoading(false);
    setError(null);
  };

  const handleAnalysisStart = () => {
    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setIsLoading(false);
    setAnalysisResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            FoodSnap AI
          </h1>
          <p className="text-lg text-gray-600">
            Upload a food image to get instant nutrition analysis
          </p>
        </header>

        <main className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            {!analysisResult && !isLoading && (
              <div className="text-center mb-8">
                <h2 className="text-2xl font-semibold text-gray-700 mb-4">
                  Take a Photo or Upload Food Image
                </h2>
                <p className="text-gray-500">
                  Our AI will identify the food and provide nutritional information for 100g portion
                </p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
                <p className="font-medium">Error:</p>
                <p>{error}</p>
              </div>
            )}

            <ImageUpload
              onAnalysisComplete={handleAnalysisComplete}
              onAnalysisStart={handleAnalysisStart}
              onError={handleError}
              isLoading={isLoading}
            />

            {isLoading && (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
                <p className="mt-4 text-gray-600">Analyzing your food image...</p>
              </div>
            )}

            {analysisResult && !isLoading && (
              <NutritionResults
                result={analysisResult}
                onReset={() => {
                  setAnalysisResult(null);
                  setError(null);
                }}
              />
            )}
          </div>
        </main>

        <footer className="text-center mt-12 text-gray-500 text-sm">
          <p>FoodSnap AI MVP - Powered by Machine Learning & USDA Nutrition Data</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
