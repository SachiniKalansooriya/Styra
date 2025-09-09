// screens/TripPlannerScreen.js
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  TextInput,
  ScrollView,
  Alert,
  Modal,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import DateTimePicker from '@react-native-community/datetimepicker';
import tripPlannerService from '../services/tripPlannerService';

const TripPlannerScreen = ({ navigation }) => {
  const [tripDetails, setTripDetails] = useState({
    destination: '',
    startDate: new Date(),
    endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
    activities: [],
    weatherExpected: '',
    packingStyle: 'minimal',
  });
  
  const [showStartDatePicker, setShowStartDatePicker] = useState(false);
  const [showEndDatePicker, setShowEndDatePicker] = useState(false);
  const [showActivitiesModal, setShowActivitiesModal] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const activities = [
    'Business Meetings',
    'Beach/Pool',
    'Hiking/Outdoor',
    'City Sightseeing',
    'Fine Dining',
    'Casual Dining',
    'Nightlife',
    'Shopping',
    'Museums/Cultural',
    'Sports/Exercise',
    'Spa/Wellness',
    'Photography',
  ];

  const packingStyles = [
    { id: 'minimal', name: 'Minimal', description: 'Pack light with versatile pieces' },
    { id: 'comfort', name: 'Comfort First', description: 'Prioritize comfort over style' },
    { id: 'fashion', name: 'Fashion Forward', description: 'Stylish outfits for every occasion' },
    { id: 'business', name: 'Business Travel', description: 'Professional with some casual items' },
  ];

  const handleActivityToggle = (activity) => {
    setTripDetails(prev => ({
      ...prev,
      activities: prev.activities.includes(activity)
        ? prev.activities.filter(a => a !== activity)
        : [...prev.activities, activity]
    }));
  };

  const handleGeneratePackingList = async () => {
    console.log('=== TRIP PLANNER DEBUG ===');
    console.log('Current tripDetails:', tripDetails);
    
    if (!tripDetails.destination.trim()) {
      Alert.alert('Missing Information', 'Please enter your destination.');
      return;
    }
    
    if (!tripDetails.weatherExpected) {
      Alert.alert('Missing Information', 'Please select the expected weather.');
      return;
    }
    
    if (tripDetails.activities.length === 0) {
      Alert.alert('Missing Information', 'Please select at least one activity.');
      return;
    }

    setLoading(true);
  
  try {
    console.log('Starting packing list generation...');
    
    const packingResult = await tripPlannerService.generateSmartPackingList(tripDetails);
    console.log('Packing result received:', packingResult);
    
    // Validate the result before navigation
    if (!packingResult) {
      throw new Error('No packing result received');
    }
    
    // Simple navigation test first
    console.log('Attempting navigation...');
    navigation.navigate('PackingListResults', { 
      tripDetails,
      packingResult
    });
    
  } catch (error) {
    console.error('Complete error details:', error);
    Alert.alert(
      'Debug Info', 
      `Error: ${error.message}\nStack: ${error.stack}`,
      [{ text: 'OK' }]
    );
  } finally {
    setLoading(false);
  }
};

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getDuration = () => {
    const diffTime = Math.abs(tripDetails.endDate - tripDetails.startDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const renderActivitiesModal = () => (
    <Modal
      visible={showActivitiesModal}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Select Activities</Text>
          <TouchableOpacity onPress={() => setShowActivitiesModal(false)}>
            <Ionicons name="close" size={24} color="#333" />
          </TouchableOpacity>
        </View>
        
        <ScrollView style={styles.modalContent}>
          {activities.map((activity) => (
            <TouchableOpacity
              key={activity}
              style={styles.activityItem}
              onPress={() => handleActivityToggle(activity)}
            >
              <Text style={styles.activityText}>{activity}</Text>
              {tripDetails.activities.includes(activity) && (
                <Ionicons name="checkmark" size={20} color="#FF8C42" />
              )}
            </TouchableOpacity>
          ))}
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Trip Planner</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Trip Details</Text>
          
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Destination</Text>
            <TextInput
              style={styles.textInput}
              placeholder="Where are you going?"
              value={tripDetails.destination}
              onChangeText={(text) => setTripDetails(prev => ({ ...prev, destination: text }))}
            />
          </View>

          <View style={styles.dateContainer}>
            <View style={styles.dateSection}>
              <Text style={styles.inputLabel}>Start Date</Text>
              <TouchableOpacity
                style={styles.dateButton}
                onPress={() => setShowStartDatePicker(true)}
              >
                <Text style={styles.dateText}>{formatDate(tripDetails.startDate)}</Text>
                <Ionicons name="calendar" size={20} color="#666" />
              </TouchableOpacity>
            </View>

            <View style={styles.dateSection}>
              <Text style={styles.inputLabel}>End Date</Text>
              <TouchableOpacity
                style={styles.dateButton}
                onPress={() => setShowEndDatePicker(true)}
              >
                <Text style={styles.dateText}>{formatDate(tripDetails.endDate)}</Text>
                <Ionicons name="calendar" size={20} color="#666" />
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.durationContainer}>
            <Text style={styles.durationText}>
              Duration: {getDuration()} {getDuration() === 1 ? 'day' : 'days'}
            </Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Expected Weather</Text>
          <View style={styles.weatherContainer}>
            {['sunny', 'rainy', 'cold', 'hot', 'mild', 'mixed'].map((weather) => (
              <TouchableOpacity
                key={weather}
                style={[
                  styles.weatherButton,
                  tripDetails.weatherExpected === weather && styles.selectedWeatherButton
                ]}
                onPress={() => setTripDetails(prev => ({ ...prev, weatherExpected: weather }))}
              >
                <Ionicons 
                  name={
                    weather === 'sunny' ? 'sunny' :
                    weather === 'rainy' ? 'rainy' :
                    weather === 'cold' ? 'snow' :
                    weather === 'hot' ? 'flame' :
                    weather === 'mild' ? 'partly-sunny' : 'cloud'
                  } 
                  size={20} 
                  color={tripDetails.weatherExpected === weather ? '#fff' : '#666'} 
                />
                <Text style={[
                  styles.weatherButtonText,
                  tripDetails.weatherExpected === weather && styles.selectedWeatherButtonText
                ]}>
                  {weather.charAt(0).toUpperCase() + weather.slice(1)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Planned Activities</Text>
          <TouchableOpacity
            style={styles.activitiesButton}
            onPress={() => setShowActivitiesModal(true)}
          >
            <Text style={styles.activitiesButtonText}>
              {tripDetails.activities.length > 0
                ? `${tripDetails.activities.length} activities selected`
                : 'Select activities for your trip'
              }
            </Text>
            <Ionicons name="chevron-forward" size={20} color="#666" />
          </TouchableOpacity>
          
          {tripDetails.activities.length > 0 && (
            <View style={styles.selectedActivities}>
              {tripDetails.activities.slice(0, 3).map((activity) => (
                <View key={activity} style={styles.activityTag}>
                  <Text style={styles.activityTagText}>{activity}</Text>
               </View>
             ))}
             {tripDetails.activities.length > 3 && (
               <View style={styles.activityTag}>
                 <Text style={styles.activityTagText}>
                   +{tripDetails.activities.length - 3} more
                 </Text>
               </View>
             )}
           </View>
         )}
       </View>

       <View style={styles.section}>
         <Text style={styles.sectionTitle}>Packing Style</Text>
         {packingStyles.map((style) => (
           <TouchableOpacity
             key={style.id}
             style={[
               styles.packingStyleItem,
               tripDetails.packingStyle === style.id && styles.selectedPackingStyle
             ]}
             onPress={() => setTripDetails(prev => ({ ...prev, packingStyle: style.id }))}
           >
             <View style={styles.packingStyleContent}>
               <Text style={[
                 styles.packingStyleName,
                 tripDetails.packingStyle === style.id && styles.selectedPackingStyleText
               ]}>
                 {style.name}
               </Text>
               <Text style={[
                 styles.packingStyleDescription,
                 tripDetails.packingStyle === style.id && styles.selectedPackingStyleText
               ]}>
                 {style.description}
               </Text>
             </View>
             {tripDetails.packingStyle === style.id && (
               <Ionicons name="checkmark-circle" size={24} color="#FF8C42" />
             )}
           </TouchableOpacity>
         ))}
       </View>

       <View style={styles.section}>
         <Text style={styles.sectionTitle}>Weather Information</Text>
         <TextInput
           style={styles.textInput}
           placeholder="Expected weather (e.g., sunny, rainy, cold...)"
           value={tripDetails.weatherExpected}
           onChangeText={(text) => setTripDetails(prev => ({ ...prev, weatherExpected: text }))}
           multiline
         />
       </View>
     </ScrollView>

     <View style={styles.bottomContainer}>
       <TouchableOpacity
         style={styles.generateButton}
         onPress={handleGeneratePackingList}
       >
         <Ionicons name="bag" size={20} color="#fff" />
         <Text style={styles.generateButtonText}>Generate Packing List</Text>
       </TouchableOpacity>
     </View>

     {showStartDatePicker && (
       <DateTimePicker
         value={tripDetails.startDate}
         mode="date"
         display="default"
         onChange={(event, selectedDate) => {
           setShowStartDatePicker(false);
           if (selectedDate) {
             setTripDetails(prev => ({ ...prev, startDate: selectedDate }));
           }
         }}
       />
     )}

     {showEndDatePicker && (
       <DateTimePicker
         value={tripDetails.endDate}
         mode="date"
         display="default"
         onChange={(event, selectedDate) => {
           setShowEndDatePicker(false);
           if (selectedDate) {
             setTripDetails(prev => ({ ...prev, endDate: selectedDate }));
           }
         }}
       />
     )}

     {renderActivitiesModal()}
   </SafeAreaView>
 );
};

const styles = StyleSheet.create({
 container: {
   flex: 1,
   backgroundColor: '#fff',
 },
 header: {
   flexDirection: 'row',
   justifyContent: 'space-between',
   alignItems: 'center',
   paddingHorizontal: 20,
   paddingVertical: 15,
   borderBottomWidth: 1,
   borderBottomColor: '#f0f0f0',
 },
 headerTitle: {
   fontSize: 20,
   fontWeight: 'bold',
   color: '#333',
 },
 content: {
   flex: 1,
 },
 section: {
   paddingHorizontal: 20,
   paddingVertical: 20,
   borderBottomWidth: 1,
   borderBottomColor: '#f0f0f0',
 },
 sectionTitle: {
   fontSize: 18,
   fontWeight: 'bold',
   color: '#333',
   marginBottom: 15,
 },
 inputContainer: {
   marginBottom: 15,
 },
 inputLabel: {
   fontSize: 14,
   fontWeight: '600',
   color: '#333',
   marginBottom: 8,
 },
 textInput: {
   borderWidth: 1,
   borderColor: '#ddd',
   borderRadius: 8,
   paddingHorizontal: 15,
   paddingVertical: 12,
   fontSize: 16,
   backgroundColor: '#f9f9f9',
 },
 dateContainer: {
   flexDirection: 'row',
   justifyContent: 'space-between',
 },
 dateSection: {
   flex: 1,
   marginHorizontal: 5,
 },
 dateButton: {
   flexDirection: 'row',
   justifyContent: 'space-between',
   alignItems: 'center',
   borderWidth: 1,
   borderColor: '#ddd',
   borderRadius: 8,
   paddingHorizontal: 15,
   paddingVertical: 12,
   backgroundColor: '#f9f9f9',
 },
 dateText: {
   fontSize: 16,
   color: '#333',
 },
 durationContainer: {
   marginTop: 10,
   alignItems: 'center',
 },
 durationText: {
   fontSize: 16,
   color: '#FF8C42',
   fontWeight: '600',
 },
 activitiesButton: {
   flexDirection: 'row',
   justifyContent: 'space-between',
   alignItems: 'center',
   borderWidth: 1,
   borderColor: '#ddd',
   borderRadius: 8,
   paddingHorizontal: 15,
   paddingVertical: 15,
   backgroundColor: '#f9f9f9',
 },
 activitiesButtonText: {
   fontSize: 16,
   color: '#333',
 },
 selectedActivities: {
   flexDirection: 'row',
   flexWrap: 'wrap',
   marginTop: 10,
 },
 activityTag: {
   backgroundColor: '#FF8C42',
   paddingHorizontal: 12,
   paddingVertical: 6,
   borderRadius: 16,
   marginRight: 8,
   marginBottom: 8,
 },
 activityTagText: {
   color: '#fff',
   fontSize: 12,
   fontWeight: '500',
 },
 packingStyleItem: {
   flexDirection: 'row',
   justifyContent: 'space-between',
   alignItems: 'center',
   paddingVertical: 15,
   paddingHorizontal: 15,
   borderWidth: 1,
   borderColor: '#ddd',
   borderRadius: 8,
   marginBottom: 10,
   backgroundColor: '#f9f9f9',
 },
 selectedPackingStyle: {
   borderColor: '#FF8C42',
   backgroundColor: '#fff5f2',
 },
 packingStyleContent: {
   flex: 1,
 },
 packingStyleName: {
   fontSize: 16,
   fontWeight: '600',
   color: '#333',
   marginBottom: 4,
 },
 packingStyleDescription: {
   fontSize: 14,
   color: '#666',
 },
 selectedPackingStyleText: {
   color: '#FF8C42',
 },
 bottomContainer: {
   paddingHorizontal: 20,
   paddingVertical: 15,
   borderTopWidth: 1,
   borderTopColor: '#f0f0f0',
 },
 generateButton: {
   backgroundColor: '#FF8C42',
   flexDirection: 'row',
   justifyContent: 'center',
   alignItems: 'center',
   paddingVertical: 15,
   borderRadius: 8,
 },
 generateButtonText: {
   color: '#fff',
   fontSize: 16,
   fontWeight: 'bold',
   marginLeft: 8,
 },
 modalContainer: {
   flex: 1,
   backgroundColor: '#fff',
 },
 modalHeader: {
   flexDirection: 'row',
   justifyContent: 'space-between',
   alignItems: 'center',
   paddingHorizontal: 20,
   paddingVertical: 15,
   borderBottomWidth: 1,
   borderBottomColor: '#f0f0f0',
 },
 modalTitle: {
   fontSize: 20,
   fontWeight: 'bold',
   color: '#333',
 },
 modalContent: {
   flex: 1,
   paddingHorizontal: 20,
 },
 activityItem: {
   flexDirection: 'row',
   justifyContent: 'space-between',
   alignItems: 'center',
   paddingVertical: 15,
   borderBottomWidth: 1,
   borderBottomColor: '#f0f0f0',
 },
 activityText: {
   fontSize: 16,
   color: '#333',
 },
 weatherContainer: {
   flexDirection: 'row',
   flexWrap: 'wrap',
   gap: 10,
 },
 weatherButton: {
   flexDirection: 'row',
   alignItems: 'center',
   backgroundColor: '#f0f0f0',
   paddingHorizontal: 12,
   paddingVertical: 8,
   borderRadius: 20,
   gap: 5,
 },
 selectedWeatherButton: {
   backgroundColor: '#FF8C42',
 },
 weatherButtonText: {
   fontSize: 14,
   color: '#666',
 },
 selectedWeatherButtonText: {
   color: '#fff',
 },
});

export default TripPlannerScreen;