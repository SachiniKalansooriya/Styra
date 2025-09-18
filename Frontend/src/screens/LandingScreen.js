import React, { useEffect } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';

const { width, height } = Dimensions.get('window');

export const LandingScreen = ({ navigation }) => {
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
          <Text style={styles.brandName}>Styra</Text>
          <Text style={styles.tagline}>Your AI-Powered Wardrobe Stylist</Text>
          <Text style={styles.description}>
            Discover perfect outfits with smart AI recommendations based on weather, occasion, and your personal style.
          </Text>
        </View>

        {/* Action Buttons */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={[styles.button, styles.primaryButton]}
            onPress={() => navigation.navigate('SignUp')}
          >
            <Text style={styles.primaryButtonText}>Get Started</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.button, styles.secondaryButton]}
            onPress={() => navigation.navigate('Login')}
          >
            <Text style={styles.secondaryButtonText}>Sign In</Text>
          </TouchableOpacity>
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
    backgroundColor: 'rgba(233, 230, 221, 0.2)', // Original color with transparency
  },
  circle2: {
    width: 150,
    height: 150,
    bottom: 100,
    left: -30,
    backgroundColor: 'rgba(221, 217, 207, 0.3)', // Darker shade
  },
  circle3: {
    width: 100,
    height: 100,
    top: height * 0.3,
    right: 20,
    backgroundColor: 'rgba(209, 205, 193, 0.25)', // Even darker shade
  },
  circle4: {
    width: 80,
    height: 80,
    top: height * 0.15,
    left: 30,
    backgroundColor: 'rgba(245, 243, 240, 0.4)', // Lighter shade
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
    color: '#5c5750', // Dark warm grey
    fontWeight: '300',
    marginBottom: 5,
  },
  brandName: {
    fontSize: 48,
    color: '#403c35', // Darkest warm brown
    fontWeight: 'bold',
    marginBottom: 10,
    textShadowColor: 'rgba(255, 255, 255, 0.3)',
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 4,
  },
  tagline: {
    fontSize: 18,
    color: '#6b6659', // Medium warm grey
    fontWeight: '500',
    marginBottom: 15,
    textAlign: 'center',
  },
  description: {
    fontSize: 16,
    color: '#7a7568', // Medium-light warm grey
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
    backgroundColor: '#d1cdc1', // Darker shade
  },
  primaryButtonText: {
    color: '#403c35', // Dark brown text
    fontSize: 18,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: '#e9e6dd', // Original color
    borderWidth: 2,
    borderColor: '#ddd9cf', // Medium shade border
  },
  secondaryButtonText: {
    color: '#5c5750', // Dark warm grey text
    fontSize: 18,
    fontWeight: '600',
  },
  skipButton: {
    alignItems: 'center',
    paddingVertical: 15,
  },
  skipText: {
    color: '#8a8577', // Medium warm grey
    fontSize: 16,
    textDecorationLine: 'underline',
  },
});