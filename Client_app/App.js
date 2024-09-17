import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View} from 'react-native';
import React, { useState, useEffect, useRef } from 'react';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import VideoStream from './VideoStream';

export default function App() {

  return (
    <View style={styles.container}>
      {/* Video stream */}
      <VideoStream url ={'http://ballretrieving.ddns.net:8000'}/>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  webStyle: {
      padding: 0,
      margin: 0,
      overflow: 'hidden'
  }
});
