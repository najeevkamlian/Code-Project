import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyDictionaryApp());
}

class MyDictionaryApp extends StatelessWidget {
  const MyDictionaryApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const DictionaryHomePage(),
    );
  }
}

class DictionaryHomePage extends StatefulWidget {
  const DictionaryHomePage({super.key});

  @override
  State<DictionaryHomePage> createState() => _DictionaryHomePageState();
}

class _DictionaryHomePageState extends State<DictionaryHomePage> {
  final FlutterTts _flutterTts = FlutterTts();
  final TextEditingController _searchController = TextEditingController();
  
  String _searchedWord = "";
  String _partOfSpeechResult = "";
  String _definitionResult = "";
  bool _isWordFound = true;
  bool _isLoading = false;

  Future<void> _searchWordFromAPI() async {
    String input = _searchController.text.trim().toLowerCase();
    if (input.isEmpty) return;

    setState(() {
      _isLoading = true;
      _searchedWord = _searchController.text;
    });

    final url = Uri.parse("https://api.dictionaryapi.dev/api/v2/entries/en/$input");

    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        
        final meanings = data[0]['meanings'][0];
        final partOfSpeech = meanings['partOfSpeech'];
        final definition = meanings['definitions'][0]['definition'];

        setState(() {
          _partOfSpeechResult = partOfSpeech;
          _definitionResult = definition;
          _isWordFound = true;
          _isLoading = false;
        });

        _speak(_searchedWord);
      } else {
        setState(() {
          _definitionResult = "Sorry, we couldn't find definitions for the word you were looking for.";
          _partOfSpeechResult = "";
          _isWordFound = false;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _definitionResult = "Error connecting to the dictionary server. Please check your internet connection.";
        _partOfSpeechResult = "";
        _isWordFound = false;
        _isLoading = false;
      });
    }
  }

  Future<void> _speak(String text) async {
    await _flutterTts.setLanguage("en-US");
    await _flutterTts.setPitch(1.0);
    await _flutterTts.speak(text);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6F9),
      appBar: AppBar(
        title: const Text('The Dictionary for the Real World', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF0056FF),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            Container(
              width: double.infinity,
              color: const Color(0xFF0056FF),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 40),
              child: TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Search any English word (try: noun, apple)...',
                  fillColor: Colors.white,
                  filled: true,
                  prefixIcon: const Icon(Icons.search, color: Colors.grey),
                  suffixIcon: Padding(
                    padding: const EdgeInsets.only(right: 4.0),
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF00E5FF),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                      ),
                      onPressed: _searchWordFromAPI,
                      child: const Text('Search', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
                    ),
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(30),
                    borderSide: BorderSide.none,
                  ),
                ),
                onSubmitted: (_) => _searchWordFromAPI(),
              ),
            ),

            const SizedBox(height: 25),

            if (_isLoading)
              const Center(child: CircularProgressIndicator(color: Color(0xFF0056FF)))
            else if (_searchedWord.isNotEmpty)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Card(
                  elevation: 4,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              _searchedWord,
                              style: TextStyle(
                                fontSize: 28,
                                fontWeight: FontWeight.bold,
                                color: _isWordFound ? const Color(0xFF0056FF) : Colors.red,
                              ),
                            ),
                            const SizedBox(width: 10),
                            if (_isWordFound)
                              IconButton(
                                icon: const Icon(Icons.volume_up, color: Color(0xFF0056FF), size: 28),
                                onPressed: () => _speak(_searchedWord),
                              ),
                          ],
                        ),
                        if (_partOfSpeechResult.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4.0),
                            child: Text(
                              _partOfSpeechResult,
                              style: const TextStyle(
                                fontSize: 16,
                                fontStyle: FontStyle.italic,
                                color: Colors.grey,
                              ),
                            ),
                          ),
                        const Divider(height: 20, thickness: 1),
                        Text(
                          _definitionResult,
                          style: TextStyle(
                            fontSize: 18, 
                            height: 1.5,
                            color: _isWordFound ? Colors.black87 : Colors.black54,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
api.dictionaryapi.dev
