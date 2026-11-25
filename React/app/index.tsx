import { useState } from 'react'
import { Image, StyleSheet, View } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { router } from 'expo-router'
import { Title } from '@/components/Title'
import { Card } from '@/components/Card'
import { Checkbox } from '@/components/Checkbox'
import { CustomButton } from '@/components/CustomButton'

export default function Home() {
  const [accepted, setAccepted] = useState(false)

  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.header}>
        <Image source={require('../assets/icon.png')} style={styles.logo} />
        <Title text="Registro" />
      </View>

      <Card text="Primera caja de texto. Aquí va el contenido con sangría dentro de su tarjeta." />

      <View style={styles.separator} />

      <Card text="Segunda caja de texto. Separada de la anterior por una línea divisoria." />

      <View style={styles.bottom}>
        <Checkbox
          label="Acepto los términos y condiciones"
          checked={accepted}
          onToggle={() => setAccepted(!accepted)}
        />

        <View style={styles.buttons}>
          <CustomButton title="Aceptar" onPress={() => router.push('/hola')} />
          <CustomButton
            title="Eliminar"
            variant="secondary"
            onPress={() => setAccepted(false)}
          />
          <CustomButton title="Contador (hook)" onPress={() => router.push('/contador')} />
        </View>
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#FFFFFF', paddingHorizontal: 24, paddingTop: 24 },
  header: { alignItems: 'center', gap: 12, marginBottom: 24 },
  logo: { width: 80, height: 80, borderRadius: 20 },
  separator: { height: 1, backgroundColor: '#D0D5DD', marginVertical: 16, marginHorizontal: 16 },
  bottom: { flex: 1, justifyContent: 'flex-end', gap: 16, paddingBottom: 24 },
  buttons: { gap: 12 },
})
