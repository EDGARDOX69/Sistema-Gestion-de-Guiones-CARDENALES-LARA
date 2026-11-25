import { StyleSheet, View } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { router } from 'expo-router'
import { Title } from '@/components/Title'
import { CustomButton } from '@/components/CustomButton'

export default function Hola() {
  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.center}>
        <Title text="Hola mundo" />
      </View>

      <View style={styles.bottom}>
        <CustomButton title="Formulario" onPress={() => router.push('/completado')} />
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#FFFFFF', padding: 24 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  bottom: { gap: 12 },
})
