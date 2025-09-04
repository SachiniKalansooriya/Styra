# Styra Backend-Frontend Connection Guide

## Current Status
✅ Backend is running successfully on your computer  
✅ Frontend has been updated with connection logic  
✅ API endpoints are working and tested  

## Connection Issues & Solutions

### The Problem
Your mobile device can't connect to `127.0.0.1:8000` because that's localhost on your computer, not accessible from the phone.

### Solutions (in order of preference)

#### Option 1: Use Expo Development Build (Recommended)
```bash
# In the Frontend directory
cd Frontend
npx expo start --tunnel
```
This creates a tunnel that allows your phone to connect to your computer.

#### Option 2: Fix Windows Firewall
1. **Allow the app through Windows Firewall:**
   - Open Windows Security → Firewall & network protection
   - Click "Allow an app through firewall"
   - Add Python or uvicorn to the allowed apps
   - Make sure both Private and Public networks are checked

2. **Test the connection:**
   ```bash
   # Test from another device on your network
   curl http://172.20.10.7:8000/
   ```

#### Option 3: Use a Different IP
Check if you have other network interfaces:
```bash
ipconfig
```
Try using a different IP address in the frontend config.

## Current Configuration

### Backend
- **Running on:** `http://0.0.0.0:8000` (accepts all connections)
- **Your IP:** `172.20.10.7:8000`
- **Status:** ✅ Working

### Frontend  
- **Primary URL:** `http://172.20.10.7:8000`
- **Fallback URL:** `http://127.0.0.1:8000`
- **Android Emulator:** `http://10.0.2.2:8000`
- **Offline Mode:** ✅ Available with mock data

## Testing the Connection

1. **Test Backend Manually:**
   ```bash
   # From your computer
   curl http://172.20.10.7:8000/
   curl http://172.20.10.7:8000/wardrobe/items
   ```

2. **Test in App:**
   - Open the app
   - Go to Home screen
   - Tap "Test Backend" button
   - Check the connection status indicator

## Available API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /wardrobe/items` - Get wardrobe items
- `POST /wardrobe/items` - Add wardrobe item  
- `GET /wardrobe/stats` - Get wardrobe statistics
- `POST /auth/login` - User login
- `POST /auth/signup` - User signup
- `POST /outfits/recommendations` - Get outfit suggestions
- `GET /weather/current` - Get weather data

## Offline Mode Features

If the backend is not reachable, the app will automatically switch to offline mode with:
- ✅ Local storage for wardrobe items
- ✅ Mock data for testing
- ✅ All UI functionality
- ✅ Camera and image processing
- ❌ Real-time AI recommendations (uses mock data)
- ❌ Weather integration (uses mock data)

## Next Steps

1. **For Development:** Use `npx expo start --tunnel`
2. **For Production:** Deploy backend to a cloud service
3. **For Testing:** Use the "Test Backend" button in the app

The app is now fully functional in both online and offline modes!
