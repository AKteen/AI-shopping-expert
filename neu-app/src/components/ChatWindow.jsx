import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';

const ChatWindow = () => {
  const [input, setInput] = useState('');
  const { messages, loading, error, sendMessage, clearMessages } = useChat();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      await sendMessage(input);
      setInput('');
    }
  };

  const ProductCard = ({ product }) => (
    <div className="bg-gray-800 border border-gray-600 rounded-lg p-3 sm:p-4 shadow-sm hover:shadow-md transition-shadow">
      <h4 className="font-semibold text-gray-100 mb-1 text-sm sm:text-xs">{product.name}</h4>
      <p className="text-xs text-gray-400 mb-1">{product.category}</p>
      <p className="text-base sm:text-sm font-bold text-blue-400 mb-1">${product.price}</p>
      <p className="text-sm sm:text-xs text-gray-300 line-clamp-2">{product.description}</p>
    </div>
  );

  const MessageBubble = ({ message }) => {
    const isUser = message.type === 'user';
    const isError = message.type === 'error';

    return (
      <div className={`flex mb-3 sm:mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
        <div className={`max-w-[85%] sm:max-w-xs lg:max-w-md px-3 sm:px-4 py-2 sm:py-3 rounded-2xl ${
          isUser 
            ? 'bg-blue-600 text-white rounded-br-md' 
            : isError 
              ? 'bg-red-900 text-red-200 border border-red-700 rounded-bl-md'
              : 'bg-gray-700 text-gray-100 rounded-bl-md'
        }`}>
          <p className="text-sm sm:text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
          
          {message.products && message.products.length > 0 && (
            <div className="mt-3 space-y-2">
              <p className="text-xs sm:text-xs font-semibold text-gray-300 mb-2">Recommended Products:</p>
              <div className="grid gap-2 sm:gap-2">
                {message.products.slice(0, 3).map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 shadow-sm border-b border-gray-700 p-3 sm:p-4">
        <div className="flex justify-between items-center max-w-4xl mx-auto">
          <h1 className="text-lg sm:text-xl lg:text-2xl font-bold text-white truncate mr-2">🛍️ AI Shopping Expert</h1>
          <button
            onClick={clearMessages}
            className="text-xs sm:text-sm text-gray-300 hover:text-white px-2 sm:px-3 py-1 rounded-md hover:bg-gray-700 transition-colors whitespace-nowrap"
          >
            Clear Chat
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-3 sm:p-4 space-y-3 sm:space-y-4">
          {messages.length === 0 && (
            <div className="text-center mt-8 sm:mt-16">
              <div className="bg-gray-800 rounded-2xl p-4 sm:p-6 lg:p-8 shadow-lg max-w-sm sm:max-w-md mx-auto border border-gray-700">
                <div className="text-3xl sm:text-4xl mb-3 sm:mb-4">👋</div>
                <h2 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3 text-white">Welcome to AI Shopping Expert!</h2>
                <p className="text-sm text-gray-300 mb-3 sm:mb-4">Ask me about products you're looking for. For example:</p>
                <div className="space-y-2 text-xs sm:text-xs text-gray-400">
                  <div className="bg-gray-700 rounded-lg p-2 text-left">"I need blue gym shoes"</div>
                  <div className="bg-gray-700 rounded-lg p-2 text-left">"Show me wireless headphones under $100"</div>
                  <div className="bg-gray-700 rounded-lg p-2 text-left">"What laptops do you recommend for students?"</div>
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {loading && (
            <div className="flex justify-start mb-3 sm:mb-4">
              <div className="bg-gray-700 rounded-2xl rounded-bl-md px-3 sm:px-4 py-2 sm:py-3 max-w-xs">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form */}
      <div className="bg-gray-800 border-t border-gray-700 p-3 sm:p-4 pb-safe">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex space-x-2 sm:space-x-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about products..."
              className="flex-1 border border-gray-600 bg-gray-700 text-white rounded-full px-4 sm:px-6 py-3 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 shadow-sm"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-blue-600 text-white px-4 sm:px-6 lg:px-8 py-3 rounded-full hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm font-medium text-sm sm:text-base min-w-[44px] flex items-center justify-center"
            >
              {loading ? '⏳' : '➤'}
            </button>
          </form>
          
          {error && (
            <p className="text-red-400 text-sm mt-2 text-center px-2">Error: {error}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;