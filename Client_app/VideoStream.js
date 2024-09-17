import React from 'react';
import { SafeAreaView, StyleSheet, View, Text } from 'react-native';
import { WebView } from 'react-native-webview';

const VideoStream = ({ url }) => {
  return (
    <SafeAreaView style={styles.container}>
      {url ? (
        <WebView
          originWhitelist={['*']}
          source={{ uri: url }}
          scrollEnabled={false}
        />
      ) : (
        <View style={styles.placeholder}>
          <Text>Connection error</Text>
        </View>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  placeholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default VideoStream;
