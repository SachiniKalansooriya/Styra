# Styra
AI-powered wardrobe stylist mobile app built with React Native

## Project Overview
Styra is an AI-powered wardrobe stylist mobile app built with React Native (Frontend) and FastAPI (Backend). It helps users analyze clothing items, manage their wardrobe, and get outfit recommendations using advanced image analysis and weather-aware styling.

### AI & Machine Learning
Styra uses advanced AI to analyze clothing images and provide smart wardrobe recommendations. The core AI component is the [CLIP (Contrastive Language–Image Pretraining)](https://openai.com/research/clip) model from OpenAI:
- **Model Used:** `openai/clip-vit-base-patch32`
- **Purpose:** Matches clothing images to text descriptions for category, color, and occasion recognition.
- **How It Works:**
    - When a user uploads a clothing photo, the backend uses CLIP to compare the image against a set of fashion categories, colors, and occasions.
    - The model outputs the best-matching category (e.g., tops, bottoms, dresses), color (e.g., red, blue, black), and occasion (e.g., casual, formal, workout).
    - These results are mapped to the wardrobe system and used for outfit recommendations.
- **Fallbacks:** If the model fails or is unavailable, the system provides default suggestions and error handling.

**AI Model Location:** See `Backend/services/deepfashion_analyzer.py` for implementation details.

### Key Features
- **AI Clothing Analysis:** Users can take photos of clothing items, which are analyzed using deep learning models (CLIP) to suggest category, color, and occasion.
- **Wardrobe Management:** Add, view, update, and delete wardrobe items with real database integration.
- **Outfit Recommendations:** Get AI-enhanced outfit suggestions based on wardrobe, weather, and user preferences.
- **History Tracking:** Keeps track of outfit and analysis history for personalized recommendations.
- **Weather Integration:** Suggests outfits suitable for current weather conditions.
- **User Authentication:** Secure login and protected screens for personalized wardrobe management.

### System Architecture
- **Frontend:** React Native app with screens for wardrobe, outfit suggestions, favorites, and more. Uses service layers for API communication and state management.
- **Backend:** FastAPI server with modular services for wardrobe, outfit history, image analysis, and weather. Integrates with a PostgreSQL database for persistent storage.
- **Image Analysis:** Utilizes DeepFashion AI models (CLIP) for advanced clothing recognition.
- **Database:** Stores wardrobe items, analysis history, and user data with robust error handling and logging.

### Typical Flow
1. User takes a photo in the app.
2. Image is sent to `/api/analyze-clothing` for AI analysis.
3. Analyzed item is automatically saved to the wardrobe.
4. Frontend fetches wardrobe items from `/api/wardrobe/items`.
5. User views and manages wardrobe in the app.

### Technologies Used
- React Native, Expo
- FastAPI, SQLAlchemy
- PostgreSQL
- DeepFashion AI models (CLIP)
- JWT Authentication
