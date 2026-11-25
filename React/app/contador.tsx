import { StyleSheet, Text, View } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { router } from 'expo-router'
import { Title } from '@/components/Title'
import { SimpleButton } from '@/components/SimpleButton'
import { useClickCounter } from '@/hooks/useClickCounter'

export default function Contador() {
  const { clicks, increment,restar, reset } = useClickCounter()

  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.center}>
        <Title text="Contador de clics" />
        <Text style={styles.count}>{clicks}</Text>
        <Text style={styles.hint}>Numeros de click </Text>
      </View>

      <View style={styles.bottom}>
        <SimpleButton label="+1 clic" onPress={increment} />
      </View>

        <View style={styles.bottom}>
        <SimpleButton label="-1 clic" onPress={restar} />
        <SimpleButton label="Reiniciar " onPress={reset} />
        <SimpleButton label="Volver" onPress={() => router.back()} />
      </View>
    </SafeAreaView>

    
  )

  
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#FFFFFF', padding: 24 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 8 },
  count: { fontSize: 64, fontWeight: '800', color: '#101828' },
  hint: { fontSize: 14, color: '#667085' },
  bottom: { gap: 12 },
})
