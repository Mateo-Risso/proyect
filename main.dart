import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

void main() => runApp(const MateoRigApp());

class MateoRigApp extends StatelessWidget {
  const MateoRigApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark, 
        primarySwatch: Colors.orange, 
        useMaterial3: true
      ),
      home: const MonitorPage(),
    );
  }
}

class MonitorPage extends StatefulWidget {
  const MonitorPage({super.key});
  @override
  State<MonitorPage> createState() => _MonitorPageState();
}

class _MonitorPageState extends State<MonitorPage> {
  // CONFIGURACIÓN: Reemplazar con tu IP local y Key real solo en tu entorno privado.
  // Para GitHub, dejamos estos valores genéricos.
  final String ipPC = "192.168.1.XX"; 
  final String apiKey = "TU_API_KEY_AQUI"; 

  String status = "Iniciando...";
  String temp = "--";
  String fan = "--";
  String power = "--";
  String cpuUsage = "--";
  String ramUsage = "--";
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    getGpuData();
    // Actualización automática cada 5 segundos para no saturar
    _timer = Timer.periodic(const Duration(seconds: 5), (timer) => getGpuData());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> getGpuData() async {
    try {
      final response = await http.get(
        Uri.parse('http://$ipPC:8000/gpu'), // Asegúrate que el puerto coincida con FastAPI
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
        },
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // Suponiendo que la API devuelve una lista de GPUs, tomamos la primera
        final gpu = data is List ? data[0] : data; 
        
        setState(() {
          temp = "${gpu['temp']}°C";
          fan = "${gpu['fan_speed']}%";
          power = "${gpu['power_draw']}W";
          status = "Online";
        });
      } else {
        setState(() => status = "Error: ${response.statusCode}");
      }
    } catch (e) {
      setState(() => status = "Offline / Sin conexión");
    }
  }

  Future<void> sendAction(String endpoint) async {
    try {
      final response = await http.post(
        Uri.parse('http://$ipPC:8000/$endpoint'),
        headers: {'x-api-key': apiKey},
      );
      
      final resData = json.decode(response.body);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(resData['message'] ?? resData['detail'] ?? "Acción enviada"))
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Error al enviar comando"))
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0E0E0E),
      appBar: AppBar(
        title: const Text("RIG MONITOR", style: TextStyle(letterSpacing: 3, fontWeight: FontWeight.bold)),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Círculo de Temperatura Principal
            Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: Colors.orange, width: 2),
                boxShadow: [
                  BoxShadow(color: Colors.orange.withOpacity(0.2), blurRadius: 20, spreadRadius: 5)
                ]
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text("GPU TEMP", style: TextStyle(color: Colors.grey, fontSize: 14)),
                  Text(temp, style: const TextStyle(fontSize: 48, fontWeight: FontWeight.bold, color: Colors.white)),
                ],
              ),
            ),
            const SizedBox(height: 40),
            // Estadísticas Secundarias
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildSmallStat("FAN", fan, Icons.toys),
                _buildSmallStat("POWER", power, Icons.bolt),
              ],
            ),
            const SizedBox(height: 40),
            // Acciones Remotas
            const Text("ACCIONES REMOTAS", style: TextStyle(letterSpacing: 2, color: Colors.grey)),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _actionButton(Icons.refresh, "reset-records", Colors.blue),
                const SizedBox(width: 20),
                _actionButton(Icons.nights_stay, "power/suspend", Colors.yellow),
                const SizedBox(width: 20),
                _actionButton(Icons.power_settings_new, "power/shutdown", Colors.red),
              ],
            ),
            const SizedBox(height: 40),
            Text(
              "Status: $status", 
              style: TextStyle(color: status == "Online" ? Colors.green : Colors.redAccent, fontWeight: FontWeight.w500)
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSmallStat(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 24, color: Colors.orange),
        const SizedBox(height: 5),
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
        Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _actionButton(IconData icon, String cmd, Color color) {
    return IconButton.filled(
      onPressed: () => sendAction(cmd),
      icon: Icon(icon),
      style: IconButton.styleFrom(
        backgroundColor: color.withOpacity(0.2),
        foregroundColor: color,
        fixedSize: const Size(60, 60),
      ),
    );
  }
}