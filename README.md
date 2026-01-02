# FoodSnap AI

A web application that identifies food from images and provides nutritional information using AI and USDA data.

## Features

- 📸 **Image Upload**: Upload food images for instant analysis
- 🤖 **AI Recognition**: Uses ResNet50 for food classification
- 🥗 **Nutrition Analysis**: Provides calories, protein, carbs, and fat data
- 📊 **USDA Integration**: Real nutrition data from USDA FoodData Central API
- 🎨 **Modern UI**: Clean, responsive interface built with React and Tailwind CSS

## Tech Stack

### Frontend
- React 18 with Vite
- Tailwind CSS for styling
- Axios for API calls

### Backend
- Python with FastAPI
- PyTorch for ML model
- Pillow for image processing
- USDA FoodData Central API integration

### AI/ML
- ResNet50 pretrained model
- Image classification and preprocessing

## Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- USDA FoodData Central API Key (optional, falls back to mock data)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd foodsnap-ai
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your USDA API key
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Start the Backend

```bash
# From backend directory
python main.py
```

The backend will start on `http://localhost:8000`

### Start the Frontend

```bash
# From frontend directory (in a new terminal)
npm run dev
```

The frontend will start on `http://localhost:3000`

## Usage

1. Open `http://localhost:3000` in your browser
2. Click "Click to upload or drag and drop" to select a food image
3. The AI will analyze the image and identify the food
4. View the nutritional information for a 100g portion
5. Click "Analyze Another Food" to process more images

## API Endpoints

### Backend Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `POST /analyze-food` - Analyze food image
  - Body: `multipart/form-data` with `file` field
  - Returns: Food name and nutrition data

## Environment Variables

### Backend (.env)

```env
# USDA FoodData Central API Key (get from https://fdc.nal.usda.gov/api-key-signup.html)
USDA_API_KEY=your_usda_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## Project Structure

```
foodsnap-ai/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUpload.jsx
│   │   │   └── NutritionResults.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── README.md
```

## How It Works

1. **Image Upload**: User uploads a food image via the React frontend
2. **Image Processing**: Backend receives and preprocesses the image
3. **AI Classification**: ResNet50 model identifies the food type
4. **Nutrition Lookup**: USDA API provides nutritional data for the identified food
5. **Results Display**: Frontend shows the food name and nutrition information

## Limitations (MVP)

- Single food item analysis only
- Fixed portion size (100g)
- Limited to 30 common food items
- Mock data fallback when USDA API is unavailable
- Basic image classification (not specialized for food)

## Getting USDA API Key

1. Visit [USDA FoodData Central](https://fdc.nal.usda.gov/api-key-signup.html)
2. Sign up for a free API key
3. Add the key to your `.env` file in the backend directory

## Troubleshooting

### Common Issues

1. **Backend won't start**: Ensure Python 3.8+ and all requirements are installed
2. **Frontend build errors**: Make sure Node.js 16+ is installed
3. **CORS errors**: Check that backend is running on port 8000
4. **API timeouts**: Large images may timeout; try smaller files (<5MB)
5. **Model loading issues**: First run may download PyTorch models (requires internet)

### Debug Mode

For debugging, you can check:
- Backend logs in terminal
- Browser console for frontend errors
- Network tab for API requests

## Future Enhancements

- Multiple food item recognition
- Custom portion size input
- User meal history
- More sophisticated food classification
- Mobile app support
- Database integration

## License

This project is for educational purposes. Please ensure compliance with USDA API terms of service.

---

**Note**: This is an MVP version. Nutrition values are estimates and should not be used for medical dietary planning.
