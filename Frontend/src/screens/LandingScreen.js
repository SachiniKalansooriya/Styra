import React, { useEffect } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  Dimensions,
  Image,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';

const { width, height } = Dimensions.get('window');

export const LandingScreen = ({ navigation, isAuthenticated = false, onLogout }) => {
  useEffect(() => {
    console.log('LandingScreen mounted with auth state:', isAuthenticated);
  }, [isAuthenticated]);

  const handleNavigate = (screenName, params = {}) => {
    try {
      console.log(`LandingScreen: navigation request -> ${screenName}`, { navigation });
      if (navigation && typeof navigation.navigate === 'function') {
        navigation.navigate(screenName, params);
      } else if (typeof navigation === 'function') {
        // support fallback where navigation itself is a function
        navigation(screenName, params);
      } else {
        console.warn('LandingScreen: navigation prop is not available');
      }
    } catch (err) {
      console.error('LandingScreen navigation error:', err);
    }
  };

  return (
    <LinearGradient 
      colors={['#f5f3f0', '#e9e6dd', '#ddd9cf', '#d1cdc1']} 
      style={styles.container}
    >
      <StatusBar style="dark" />
      
      {/* Background Pattern */}
      <View style={styles.backgroundPattern}>
        <View style={[styles.circle, styles.circle1]} />
        <View style={[styles.circle, styles.circle2]} />
        <View style={[styles.circle, styles.circle3]} />
        <View style={[styles.circle, styles.circle4]} />
      </View>

      <View style={styles.content}>

        {/* Title Section */}
        <View style={styles.titleContainer}>
          <Text style={styles.title}>Welcome to</Text>
          <Image
            source={require('../../assets/styraicon.png')}
            style={styles.brandLogo}
            accessibilityLabel="Styra logo"
            resizeMode="contain"
          />
          <Text style={styles.tagline}>Your AI-Powered Wardrobe Stylist</Text>
          <Text style={styles.description}>
            Discover perfect outfits with smart AI recommendations based on weather, occasion, and your personal style.
          </Text>
        </View>

        {/* Action Buttons - Always show Create Account and Login */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={[styles.button, styles.primaryButton]}
            onPress={() => handleNavigate('SignUp')}
          >
            <Text style={styles.primaryButtonText}>Create Account</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.button, styles.secondaryButton]}
            onPress={() => handleNavigate('Login')}
          >
            <Text style={styles.secondaryButtonText}>Login</Text>
          </TouchableOpacity>

          {/* Optional: Show sign out option if user is authenticated */}
          {isAuthenticated && (
            <TouchableOpacity 
              style={styles.skipButton}
              onPress={() => {
                if (onLogout) {
                  onLogout();
                }
              }}
            >
              <Text style={styles.skipText}>Sign Out</Text>
            </TouchableOpacity>
          )}
        </View>

      </View>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  backgroundPattern: {
    position: 'absolute',
    width: '100%',
    height: '100%',
  },
  circle: {
    position: 'absolute',
    borderRadius: 1000,
  },
  circle1: {
    width: 200,
    height: 200,
    top: -50,
    right: -50,
    backgroundColor: 'rgba(233, 230, 221, 0.2)',
  },
  circle2: {
    width: 150,
    height: 150,
    bottom: 100,
    left: -30,
    backgroundColor: 'rgba(221, 217, 207, 0.3)',
  },
  circle3: {
    width: 100,
    height: 100,
    top: height * 0.3,
    right: 20,
    backgroundColor: 'rgba(209, 205, 193, 0.25)',
  },
  circle4: {
    width: 80,
    height: 80,
    top: height * 0.15,
    left: 30,
    backgroundColor: 'rgba(245, 243, 240, 0.4)',
  },
  content: {
    flex: 1,
    paddingHorizontal: 30,
    justifyContent: 'center',
  },
  titleContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 24,
    color: '#5c5750',
    fontWeight: '300',
    marginBottom: 1,
  },
  brandLogo: {
    width: 300,
    height: 300,
    marginBottom: 10,
  },
  tagline: {
    fontSize: 18,
    color: '#6b6659',
    fontWeight: '500',
    marginBottom: 15,
    textAlign: 'center',
  },
  description: {
    fontSize: 16,
    color: '#7a7568',
    textAlign: 'center',
    lineHeight: 24,
    paddingHorizontal: 10,
  },
  buttonContainer: {
    width: '100%',
  },
  button: {
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 25,
    marginBottom: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
    elevation: 8,
  },
  primaryButton: {
    backgroundColor: '#d1cdc1',
  },
  primaryButtonText: {
    color: '#403c35',
    fontSize: 18,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: '#e9e6dd',
    borderWidth: 2,
    borderColor: '#ddd9cf',
  },
  secondaryButtonText: {
    color: '#5c5750',
    fontSize: 18,
    fontWeight: '600',
  },
  skipButton: {
    alignItems: 'center',
    paddingVertical: 15,
  },
  skipText: {
    color: '#8a8577',
    fontSize: 16,
    textDecorationLine: 'underline',
  },
});