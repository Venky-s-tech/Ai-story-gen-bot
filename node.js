import React, { useState, useEffect } from 'react';
import { ChevronRight, Loader2, Volume2, Download, X, Camera, Type } from 'lucide-react';

// Simulated API functions (replace with your actual API endpoints)
const generateStoryFromText = async (prompt) => {
  // Replace with your actual API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve("Generated story based on: " + prompt);
    }, 3000);
  });
};

const generateImageCaption = async (imageFile) => {
  // Replace with your actual image caption API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve("A descriptive caption of the uploaded image");
    }, 2000);
  });
};

const generateAudioFromStory = async (text) => {
  // Replace with your actual audio generation API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve("story_audio.mp3");
    }, 2000);
  });
};

const StoryApp = () => {
  // State management
  const [generatedStory, setGeneratedStory] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [inputText, setInputText] = useState('As the rain poured down on a quiet, dimly lit street, I found myself standing in front of a quaint bookstore');
  const [selectedTheme, setSelectedTheme] = useState('Horror');
  const [inputType, setInputType] = useState('text');
  const [uploadedImage, setUploadedImage] = useState(null);
  const [showGenerator, setShowGenerator] = useState(false);
  const [audioUrl, setAudioUrl] = useState('');
  const [generationError, setGenerationError] = useState('');

  const categories = [
    {
      title: 'Hot Now',
      stories: [
        { title: 'Star-Crossed', image: '/api/placeholder/200/300', rating: '4.8' },
        { title: 'The Dance', image: '/api/placeholder/200/300', rating: '4.6' },
        { title: 'Night Tales', image: '/api/placeholder/200/300', rating: '4.7' }
      ]
    },
    {
      title: 'Romance',
      stories: [
        { title: 'The Dance', image: '/api/placeholder/200/300', rating: '4.5' },
        { title: 'Making it All', image: '/api/placeholder/200/300', rating: '4.3' },
        { title: 'Last Love', image: '/api/placeholder/200/300', rating: '4.4' }
      ]
    },
    // Add more categories as needed
  ];

  const themePrompts = {
    "Horror": "Write a horror story using:",
    "Action": "Write a story with lots of action using: ",
    "Romance": "Write a romantic story using: ",
    "Comedy": "Write a funny story using: ",
    "Historical": "Write a story based on a historical event with the help of the input: ",
    "Science Fiction": "Write a science fiction story using: "
  };

  const handleGenerateStory = async () => {
    setIsGenerating(true);
    setGenerationError('');
    try {
      let story;
      if (inputType === 'text') {
        const prompt = themePrompts[selectedTheme] + " " + inputText;
        story = await generateStoryFromText(prompt);
      } else {
        if (!uploadedImage) {
          throw new Error('Please upload an image first');
        }
        const caption = await generateImageCaption(uploadedImage);
        const prompt = themePrompts[selectedTheme] + " " + caption;
        story = await generateStoryFromText(prompt);
      }
      
      setGeneratedStory(story);
      // Generate audio after story is generated
      setIsGeneratingAudio(true);
      const audioFileUrl = await generateAudioFromStory(story);
      setAudioUrl(audioFileUrl);
      setIsGeneratingAudio(false);
    } catch (error) {
      setGenerationError(error.message || 'Error generating story');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type !== 'image/jpeg' && file.type !== 'image/png') {
        setGenerationError('Please upload a JPG or PNG image');
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const downloadStory = () => {
    const element = document.createElement("a");
    const file = new Blob([generatedStory], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = "generated_story.txt";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="fixed top-0 w-full z-40 bg-gradient-to-b from-black/80 to-transparent">
        <div className="flex items-center justify-between p-4">
          <h1 className="text-2xl font-bold">AI Story</h1>
          <div className="flex items-center space-x-4">
            <button className="p-2">Search</button>
            <button className="p-2">Profile</button>
          </div>
        </div>
        <div className="px-4 pb-4">
          <button 
            className="bg-white text-black px-6 py-2 rounded-md font-semibold"
            onClick={() => setShowGenerator(true)}
          >
            Generate Story
          </button>
        </div>
      </div>

      {/* Story Generator Modal */}
      {showGenerator && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-gray-900 rounded-lg p-6 max-w-2xl w-full relative">
            <button 
              className="absolute top-4 right-4"
              onClick={() => setShowGenerator(false)}
            >
              <X className="h-6 w-6" />
            </button>

            <h2 className="text-xl font-bold mb-6">Create Your Story</h2>

            {/* Input Type Selection */}
            <div className="flex space-x-4 mb-6">
              <button 
                className={`flex items-center px-4 py-2 rounded-md ${inputType === 'text' ? 'bg-white text-black' : 'bg-gray-800'}`}
                onClick={() => setInputType('text')}
              >
                <Type className="mr-2 h-4 w-4" />
                Text
              </button>
              <button 
                className={`flex items-center px-4 py-2 rounded-md ${inputType === 'image' ? 'bg-white text-black' : 'bg-gray-800'}`}
                onClick={() => setInputType('image')}
              >
                <Camera className="mr-2 h-4 w-4" />
                Image
              </button>
            </div>

            {/* Theme Selection */}
            <select 
              className="w-full p-3 mb-4 bg-gray-800 rounded-md"
              value={selectedTheme}
              onChange={(e) => setSelectedTheme(e.target.value)}
            >
              {Object.keys(themePrompts).map(theme => (
                <option key={theme} value={theme}>{theme}</option>
              ))}
            </select>

            {/* Input Area */}
            {inputType === 'text' ? (
              <textarea
                className="w-full p-4 mb-4 bg-gray-800 rounded-md h-32"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Enter your story prompt..."
              />
            ) : (
              <div className="mb-4">
                <input
                  type="file"
                  accept="image/jpeg,image/png"
                  onChange={handleImageUpload}
                  className="hidden"
                  id="image-upload"
                />
                <label 
                  htmlFor="image-upload"
                  className="block w-full p-4 bg-gray-800 rounded-md text-center cursor-pointer hover:bg-gray-700"
                >
                  {uploadedImage ? 'Change Image' : 'Upload Image'}
                </label>
                {uploadedImage && (
                  <img 
                    src={uploadedImage} 
                    alt="Uploaded" 
                    className="mt-4 max-h-48 mx-auto rounded-md"
                  />
                )}
              </div>
            )}

            {generationError && (
              <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded-md text-red-200">
                {generationError}
              </div>
            )}

            <button
              className="w-full bg-white text-black px-6 py-3 rounded-md font-semibold mb-4"
              onClick={handleGenerateStory}
              disabled={isGenerating || isGeneratingAudio}
            >
              {isGenerating ? (
                <span className="flex items-center justify-center">
                  <Loader2 className="animate-spin mr-2" />
                  Generating Story...
                </span>
              ) : isGeneratingAudio ? (
                <span className="flex items-center justify-center">
                  <Loader2 className="animate-spin mr-2" />
                  Generating Audio...
                </span>
              ) : 'Generate'}
            </button>

            {/* Generated Story Display */}
            {generatedStory && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-2">Your Story:</h3>
                <div className="bg-gray-800 p-4 rounded-md whitespace-pre-line mb-4">
                  {generatedStory}
                </div>
                
                <div className="flex flex-wrap gap-4">
                  <button
                    className="flex items-center px-4 py-2 bg-gray-800 rounded-md hover:bg-gray-700"
                    onClick={downloadStory}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download Story
                  </button>
                  
                  {audioUrl && (
                    <button
                      className="flex items-center px-4 py-2 bg-gray-800 rounded-md hover:bg-gray-700"
                    >
                      <Volume2 className="mr-2 h-4 w-4" />
                      Play Audio
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="pt-32 pb-16">
        {/* Featured Story */}
        <div className="relative h-[70vh] mb-8">
          <div className="absolute inset-0">
            <img 
              src="/api/placeholder/1200/800" 
              alt="Featured Story"
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent" />
          </div>
          <div className="absolute bottom-0 left-0 p-8">
            <h2 className="text-4xl font-bold mb-4">Man & Wolf</h2>
            <p className="text-lg mb-4 max-w-xl">A tale of loyalty and survival in a harsh winter landscape.</p>
          </div>
        </div>

        {/* Categories */}
        {categories.map((category) => (
          <div key={category.title} className="mb-8">
            <div className="px-8 mb-4 flex items-center justify-between">
              <h3 className="text-xl font-semibold">{category.title}</h3>
              <button className="text-sm flex items-center opacity-80 hover:opacity-100">
                All <ChevronRight className="h-4 w-4" />
              </button>
            </div>
            <div className="relative">
              <div className="flex space-x-4 overflow-x-auto px-8 pb-4 hide-scrollbar">
                {category.stories.map((story) => (
                  <div 
                    key={story.title} 
                    className="flex-none w-[200px] group cursor-pointer"
                  >
                    <div className="relative aspect-[2/3] rounded-md overflow-hidden mb-2">
                      <img 
                        src={story.image} 
                        alt={story.title}
                        className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-200"
                      />
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
                        <button 
                          className="bg-white/90 text-black px-4 py-2 rounded-md text-sm font-medium"
                          onClick={() => {
                            setShowGenerator(true);
                            setInputText(story.title);
                          }}
                        >
                          Generate
                        </button>
                      </div>
                    </div>
                    <h4 className="text-sm font-medium">{story.title}</h4>
                    <div className="text-xs text-gray-400">Rating: {story.rating}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 w-full bg-black/90 border-t border-gray-800">
        <div className="flex justify-around py-4">
          <button className="text-sm opacity-80 hover:opacity-100">Home</button>
          <button className="text-sm opacity-80 hover:opacity-100">My Stories</button>
          <button className="text-sm opacity-80 hover:opacity-100">Profile</button>
        </div>
      </nav>

      <style jsx global>{`
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
};

export default StoryApp;