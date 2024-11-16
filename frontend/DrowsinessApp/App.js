import React, { useState, useEffect } from 'react';
import { View, Text, Alert, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons as Icon } from '@expo/vector-icons';
import LottieViewNative from 'lottie-react-native';  // Native Lottie package for mobile
import LottieWeb from 'lottie-react';  // Web-compatible Lottie package

const SERVER_URL = "http://localhost:5000";

export default function App() {
  const [driving, setDriving] = useState(false);
  const [drowsinessAlert, setDrowsinessAlert] = useState(false);

  // Conditional import for web or mobile Lottie
  const LottieView = Platform.OS === 'web' ? LottieWeb : LottieViewNative;

  const startDriving = async () => {
    setDriving(true);
    try {
      await fetch(`${SERVER_URL}/start_session`, { method: "POST" });
      Alert.alert("Session started", "Drive safely!");
    } catch (error) {
      console.error("Error starting session:", error);
    }
  };

  const stopDriving = async () => {
    setDriving(false);
    setDrowsinessAlert(false);
    try {
      await fetch(`${SERVER_URL}/stop_session`, { method: "POST" });
      Alert.alert("Session ended", "Thank you for using the app!");
    } catch (error) {
      console.error("Error stopping session:", error);
    }
  };

  useEffect(() => {
    let interval;
    if (driving) {
      interval = setInterval(() => {
        fetch(`${SERVER_URL}/check_drowsiness`)
          .then(response => response.json())
          .then(data => {
            if (data.alert && !drowsinessAlert) {
              setDrowsinessAlert(true);
              Alert.alert("Drowsiness Detected", "Please stay alert!");
            } else if (!data.alert) {
              setDrowsinessAlert(false);
            }
          })
          .catch(error => console.error("Error fetching drowsiness status:", error));
      }, 5000);
    }
    return () => clearInterval(interval);
  }, [driving, drowsinessAlert]);

  return (
    <LinearGradient colors={['#2a2a72', '#009ffd']} style={styles.gradient}>
      <View style={styles.container}>
        <Text style={styles.title}>🚗 Drowsiness Detection</Text>

        <TouchableOpacity
          style={[styles.button, driving ? styles.stopButton : styles.startButton]}
          onPress={driving ? stopDriving : startDriving}
        >
          <Icon name={driving ? "car-off" : "car"} size={28} color="#fff" />
          <Text style={styles.buttonText}>{driving ? "Stop Driving" : "Start Driving"}</Text>
        </TouchableOpacity>

        {drowsinessAlert && (
          <Text style={styles.alert}>⚠️ Drowsiness Detected!</Text>
        )}

        {driving && (
          <LottieView
            animationData={require('./car_animation.json')} // Use this for Web
            autoPlay
            loop
            style={styles.carAnimation}
          />
        )}
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: {
    flex: 1,
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 40,
    textAlign: 'center',
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 40,
    borderRadius: 30,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3.5,
    elevation: 5,
    marginBottom: 20,
  },
  startButton: {
    backgroundColor: '#1e88e5',
  },
  stopButton: {
    backgroundColor: '#e53935',
  },
  buttonText: {
    fontSize: 18,
    color: '#fff',
    fontWeight: '600',
    marginLeft: 10,
  },
  alert: {
    color: '#ffeb3b',
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 20,
    textAlign: 'center',
  },
  carAnimation: {
    width: 300,
    height: 300,
    marginTop: 20,
  },
});
