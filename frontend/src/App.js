import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Import Shadcn components
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Search, BookOpen, User, Heart, Sparkles, Moon, Sun } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Theme context for dark/light mode
const ThemeContext = React.createContext();

function App() {
  const [darkMode, setDarkMode] = useState(false);

  return (
    <ThemeContext.Provider value={{ darkMode, setDarkMode }}>
      <div className={`App ${darkMode ? 'dark' : ''}`}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/poets" element={<PoetsPage />} />
            <Route path="/poet/:poetId" element={<PoetDetailsPage />} />
            <Route path="/poem/:poemId" element={<PoemPage />} />
          </Routes>
        </BrowserRouter>
      </div>
    </ThemeContext.Provider>
  );
}

// Homepage Component
const HomePage = () => {
  const [poets, setPoets] = useState([]);
  const [poems, setPoems] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const { darkMode, setDarkMode } = React.useContext(ThemeContext);

  useEffect(() => {
    loadData();
    initSampleData();
  }, []);

  const loadData = async () => {
    try {
      const [poetsRes, poemsRes] = await Promise.all([
        axios.get(`${API}/poets`),
        axios.get(`${API}/poems`)
      ]);
      setPoets(poetsRes.data.slice(0, 6));
      setPoems(poemsRes.data.slice(0, 8));
    } catch (error) {
      console.error('خطأ في تحميل البيانات:', error);
    }
  };

  const initSampleData = async () => {
    try {
      await axios.post(`${API}/init-data`);
    } catch (error) {
      console.error('البيانات التجريبية موجودة مسبقاً');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const response = await axios.get(`${API}/search?q=${encodeURIComponent(searchQuery)}`);
      setSearchResults(response.data);
    } catch (error) {
      console.error('خطأ في البحث:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-amber-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <BookOpen className="h-8 w-8 text-amber-600 dark:text-amber-400" />
              <h1 className="text-2xl font-bold text-gray-800 dark:text-white font-amiri">
                ديوان الشعر العربي
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setDarkMode(!darkMode)}
                className="text-gray-600 dark:text-gray-300"
              >
                {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto text-center">
          <h2 className="text-5xl font-bold text-gray-800 dark:text-white mb-6 font-amiri leading-relaxed">
            اكتشف كنوز الشعر العربي
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto leading-relaxed">
            منصة تفاعلية تجمع أعظم قصائد الشعر العربي مع شرح ذكي للكلمات والمعاني
          </p>
          
          {/* Search Bar */}
          <div className="max-w-2xl mx-auto">
            <div className="flex gap-2 bg-white dark:bg-gray-800 rounded-full p-2 shadow-xl border border-amber-200 dark:border-gray-700">
              <Input
                type="text"
                placeholder="ابحث عن شاعر أو قصيدة أو كلمة..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="flex-1 border-0 focus:ring-0 text-right bg-transparent text-gray-800 dark:text-white"
              />
              <Button onClick={handleSearch} className="rounded-full bg-amber-600 hover:bg-amber-700 dark:bg-amber-500 dark:hover:bg-amber-600">
                <Search className="h-5 w-5" />
              </Button>
            </div>
          </div>

          {/* Search Results */}
          {searchResults && (
            <div className="mt-8 max-w-4xl mx-auto">
              <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-amber-200 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="text-right text-gray-800 dark:text-white">نتائج البحث</CardTitle>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="poems" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="poems">القصائد ({searchResults.poems?.length || 0})</TabsTrigger>
                      <TabsTrigger value="poets">الشعراء ({searchResults.poets?.length || 0})</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="poems" className="mt-4">
                      <div className="grid gap-4">
                        {searchResults.poems?.map(poem => (
                          <PoemCard key={poem.id} poem={poem} />
                        ))}
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="poets" className="mt-4">
                      <div className="grid gap-4">
                        {searchResults.poets?.map(poet => (
                          <PoetCard key={poet.id} poet={poet} />
                        ))}
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </section>

      {/* Featured Poets */}
      <section className="py-16 px-6">
        <div className="container mx-auto">
          <h3 className="text-3xl font-bold text-center text-gray-800 dark:text-white mb-12 font-amiri">
            شعراء مميزون
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {poets.map(poet => (
              <PoetCard key={poet.id} poet={poet} />
            ))}
          </div>
        </div>
      </section>

      {/* Featured Poems */}
      <section className="py-16 px-6 bg-white/30 dark:bg-gray-800/30">
        <div className="container mx-auto">
          <h3 className="text-3xl font-bold text-center text-gray-800 dark:text-white mb-12 font-amiri">
            قصائد مختارة
          </h3>
          <div className="grid md:grid-cols-2 gap-8">
            {poems.map(poem => (
              <PoemCard key={poem.id} poem={poem} />
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 dark:bg-gray-900 text-white py-12">
        <div className="container mx-auto px-6 text-center">
          <div className="flex items-center justify-center space-x-4 mb-6">
            <BookOpen className="h-8 w-8 text-amber-400" />
            <h4 className="text-2xl font-bold font-amiri">ديوان الشعر العربي</h4>
          </div>
          <p className="text-gray-400 mb-4">
            منصة تفاعلية لاستكشاف وفهم كنوز الشعر العربي
          </p>
          <p className="text-gray-500 text-sm">
            © 2025 جميع الحقوق محفوظة
          </p>
        </div>
      </footer>
    </div>
  );
};

// Poet Card Component
const PoetCard = ({ poet }) => (
  <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-amber-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 hover:scale-105">
    <CardContent className="p-6">
      <div className="flex items-center space-x-4 text-right">
        <div className="flex-1">
          <h4 className="text-xl font-bold text-gray-800 dark:text-white mb-2 font-amiri">
            {poet.name}
          </h4>
          <Badge variant="secondary" className="mb-3 bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200">
            {poet.era}
          </Badge>
          <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
            {poet.bio.substring(0, 120)}...
          </p>
          <div className="mt-4">
            <Button 
              variant="outline" 
              size="sm"
              className="border-amber-300 dark:border-amber-600 text-amber-700 dark:text-amber-300 hover:bg-amber-50 dark:hover:bg-amber-900"
            >
              <User className="h-4 w-4 ml-2" />
              عرض أعمال الشاعر
            </Button>
          </div>
        </div>
        {poet.image_url && (
          <img 
            src={poet.image_url} 
            alt={poet.name}
            className="w-16 h-16 rounded-full object-cover border-2 border-amber-300 dark:border-amber-600"
          />
        )}
      </div>
    </CardContent>
  </Card>
);

// Poem Card Component
const PoemCard = ({ poem }) => (
  <PoemDialog poem={poem}>
    <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-amber-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 cursor-pointer hover:scale-105">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="text-right flex-1">
            <CardTitle className="text-gray-800 dark:text-white font-amiri text-xl mb-2">
              {poem.title}
            </CardTitle>
            <CardDescription className="text-gray-600 dark:text-gray-300">
              {poem.poet_name}
            </CardDescription>
          </div>
          <Badge variant="outline" className="border-amber-300 dark:border-amber-600 text-amber-700 dark:text-amber-300">
            {poem.theme}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-right">
          <p className="text-gray-700 dark:text-gray-200 leading-relaxed font-amiri text-lg mb-4">
            {poem.content.split('\n')[0]}...
          </p>
          <Button variant="ghost" size="sm" className="text-amber-600 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-900">
            <Sparkles className="h-4 w-4 ml-2" />
            اقرأ القصيدة كاملة
          </Button>
        </div>
      </CardContent>
    </Card>
  </PoemDialog>
);

// Poem Dialog with Word Explanation
const PoemDialog = ({ poem, children }) => {
  const [explanation, setExplanation] = useState(null);
  const [loadingWord, setLoadingWord] = useState(null);

  const explainWord = async (word, context) => {
    setLoadingWord(word);
    try {
      const response = await axios.post(`${API}/explain-word`, {
        word,
        context,
        poem_title: poem.title,
        poet_name: poem.poet_name
      });
      setExplanation(response.data);
    } catch (error) {
      console.error('خطأ في شرح الكلمة:', error);
      setExplanation({
        word,
        context,
        explanation: 'عذراً، حدث خطأ في شرح هذه الكلمة. يرجى المحاولة مرة أخرى.'
      });
    } finally {
      setLoadingWord(null);
    }
  };

  const renderPoetryWithClickableWords = (text) => {
    const lines = text.split('\n');
    return lines.map((line, lineIndex) => (
      <div key={lineIndex} className="mb-4 text-center">
        {line.split(' ').map((word, wordIndex) => (
          <span
            key={wordIndex}
            className="inline-block mx-1 px-1 py-0.5 rounded hover:bg-amber-100 dark:hover:bg-amber-900 cursor-pointer transition-colors duration-200 text-amber-800 dark:text-amber-200 hover:text-amber-900 dark:hover:text-amber-100"
            onClick={() => explainWord(word.replace(/[^\u0600-\u06FF\u0750-\u077F]/g, ''), line)}
          >
            {word}
          </span>
        ))}
      </div>
    ));
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto bg-white dark:bg-gray-800">
        <DialogHeader className="text-right">
          <DialogTitle className="text-2xl font-amiri text-gray-800 dark:text-white">
            {poem.title}
          </DialogTitle>
          <DialogDescription className="text-gray-600 dark:text-gray-300">
            بقلم: {poem.poet_name} • {poem.theme}
            {poem.meter && ` • البحر: ${poem.meter}`}
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid md:grid-cols-3 gap-6 mt-6">
          {/* Poetry Text */}
          <div className="md:col-span-2">
            <div className="bg-amber-50 dark:bg-gray-700 rounded-lg p-6 border-2 border-amber-200 dark:border-gray-600">
              <div className="text-xl leading-loose font-amiri text-gray-800 dark:text-gray-200">
                {renderPoetryWithClickableWords(poem.content)}
              </div>
              <p className="text-sm text-amber-600 dark:text-amber-400 mt-4 text-center italic">
                اضغط على أي كلمة لمعرفة معناها
              </p>
            </div>
          </div>
          
          {/* Word Explanation Panel */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 border-2 border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 text-right font-amiri">
              شرح الكلمات
            </h3>
            
            {loadingWord && (
              <div className="text-center text-amber-600 dark:text-amber-400">
                <Sparkles className="h-6 w-6 animate-spin mx-auto mb-2" />
                <p>جارٍ شرح كلمة "{loadingWord}"...</p>
              </div>
            )}
            
            {explanation ? (
              <div className="space-y-4">
                <div>
                  <h4 className="font-bold text-amber-600 dark:text-amber-400 text-right">
                    الكلمة: {explanation.word}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300 text-right mt-1">
                    السياق: {explanation.context}
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-600 rounded-lg p-4 border border-amber-200 dark:border-gray-500">
                  <p className="text-gray-800 dark:text-gray-200 text-right leading-relaxed">
                    {explanation.explanation}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setExplanation(null)}
                  className="w-full"
                >
                  مسح الشرح
                </Button>
              </div>
            ) : (
              <div className="text-center text-gray-500 dark:text-gray-400">
                <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-sm">
                  اضغط على أي كلمة في القصيدة لمعرفة معناها وشرحها
                </p>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Other page components (simplified for now)
const PoetsPage = () => <div>صفحة الشعراء</div>;
const PoetDetailsPage = () => <div>تفاصيل الشاعر</div>;
const PoemPage = () => <div>صفحة القصيدة</div>;

export default App;