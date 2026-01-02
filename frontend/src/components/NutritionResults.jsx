import React from 'react';

const NutritionResults = ({ result, onReset }) => {
  const { food_name, portion_size, nutrition, confidence } = result;

  const formatNutrient = (value, unit = 'g') => {
    return `${typeof value === 'number' ? value.toFixed(1) : value} ${unit}`;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceText = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="nutrition-card space-y-6">
      {/* Food Identification */}
      <div className="text-center pb-6 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 capitalize mb-2">
          {food_name.replace('_', ' ')}
        </h2>
        <p className="text-gray-600 mb-3">
          Portion: {portion_size}
        </p>
        <div className="flex items-center justify-center space-x-2">
          <span className="text-sm text-gray-500">Confidence:</span>
          <span className={`text-sm font-medium ${getConfidenceColor(confidence)}`}>
            {getConfidenceText(confidence)} ({Math.round(confidence * 100)}%)
          </span>
        </div>
      </div>

      {/* Nutrition Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-800 mb-4">Macronutrients</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-700 font-medium">Protein</span>
              <span className="text-gray-900 font-bold">
                {formatNutrient(nutrition.protein)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-700 font-medium">Carbohydrates</span>
              <span className="text-gray-900 font-bold">
                {formatNutrient(nutrition.carbs)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-700 font-medium">Fat</span>
              <span className="text-gray-900 font-bold">
                {formatNutrient(nutrition.fat)}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-green-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-800 mb-4">Energy</h3>
          <div className="text-center">
            <div className="text-4xl font-bold text-green-600">
              {Math.round(nutrition.calories)}
            </div>
            <div className="text-gray-600 mt-1">calories</div>
          </div>
        </div>
      </div>

      {/* Additional Information */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            <strong>Data Source:</strong> {nutrition.source.replace('_', ' ').toUpperCase()}
          </div>
          <div className="text-sm text-gray-500">
            Analysis for 100g portion
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4 pt-4">
        <button
          onClick={onReset}
          className="px-6 py-3 bg-green-500 text-white font-medium rounded-lg hover:bg-green-600 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
        >
          Analyze Another Food
        </button>
      </div>

      {/* Disclaimer */}
      <div className="text-center text-xs text-gray-500 pt-4 border-t border-gray-200">
        <p>
          This is an MVP version. Nutrition values are estimates for educational purposes only.
          Always consult professional nutritionists for dietary advice.
        </p>
      </div>
    </div>
  );
};

export default NutritionResults;
