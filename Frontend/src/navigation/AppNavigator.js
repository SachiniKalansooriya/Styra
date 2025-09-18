import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import { LandingScreen } from '../screens/LandingScreen';
import { LoginScreen } from '../screens/LoginScreen';
import { SignUpScreen } from '../screens/SignUpScreen';
import HomeScreen from '../screens/HomeScreen';
import { AddClothesScreen } from '../screens/AddClothesScreen';
import MyWardrobeScreen from '../screens/MyWardrobeScreen';
import TripPlannerScreen from '../screens/TripPlannerScreen';
import GetOutfitScreen from '../screens/GetOutfitScreen';
import PackingListResultsScreen from '../screens/PackingListResultsScreen';
import OutfitHistoryScreen from '../screens/OutfitHistoryScreen';
// Import with explicit naming
import FavoriteOutfitsScreen from '../screens/FavoriteOutfitsScreen';

const Stack = createStackNavigator();

export const AppNavigator = () => {
  console.log('AppNavigator initialized');
  
  return (
    <NavigationContainer>
      <Stack.Navigator 
        initialRouteName="Landing"
        screenOptions={{
          headerShown: false,
          gestureEnabled: true,
          gestureDirection: 'horizontal',
          cardStyleInterpolator: ({ current, layouts }) => {
            return {
              cardStyle: {
                transform: [
                  {
                    translateX: current.progress.interpolate({
                      inputRange: [0, 1],
                      outputRange: [layouts.screen.width, 0],
                    }),
                  },
                ],
              },
            };
          },
        }}
      >
        <Stack.Screen name="Landing" component={LandingScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="SignUp" component={SignUpScreen} />
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="AddClothes" component={AddClothesScreen} />
        <Stack.Screen name="MyWardrobe" component={MyWardrobeScreen} />
        <Stack.Screen name="TripPlanner" component={TripPlannerScreen} />
        <Stack.Screen name="GetOutfit" component={GetOutfitScreen} />
        <Stack.Screen name="PackingListResults" component={PackingListResultsScreen} />
        <Stack.Screen name="OutfitHistory" component={OutfitHistoryScreen} />
        <Stack.Screen 
          name="FavoriteOutfits" 
          component={FavoriteOutfitsScreen} 
          options={{ headerShown: false }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};