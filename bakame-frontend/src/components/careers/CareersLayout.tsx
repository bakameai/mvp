
interface CareersLayoutProps {
  children: React.ReactNode;
}

const CareersLayout = ({ children }: CareersLayoutProps) => {
  return (
    <div className="min-h-screen text-white bg-slate-950">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 md:p-8 border-b border-gray-800">
        <div className="text-2xl font-bold text-white">Bakame AI</div>
        <div className="hidden md:flex space-x-8">
          <a href="/" className="text-gray-300 hover:text-white transition-colors duration-200">Home</a>
          <a href="/blog" className="text-gray-300 hover:text-white transition-colors duration-200">Blog</a>
          <a href="/resources" className="text-gray-300 hover:text-white transition-colors duration-200">Resources</a>
          <a href="/team" className="text-white font-medium border-b-2 border-blue-500">Careers</a>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-16">
        {children}
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-12">
        <div className="max-w-4xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center">
          <div className="text-xl font-bold text-white mb-4 md:mb-0">Bakame AI</div>
          <div className="flex space-x-8 text-gray-300">
            <a href="/" className="hover:text-white transition-colors duration-200">Home</a>
            <a href="/blog" className="hover:text-white transition-colors duration-200">Blog</a>
            <a href="/resources" className="hover:text-white transition-colors duration-200">Resources</a>
            <a href="/team" className="hover:text-white transition-colors duration-200">Careers</a>
          </div>
        </div>
        <div className="max-w-4xl mx-auto px-6 mt-8 pt-8 border-t border-gray-800 text-center text-gray-400">
          <p>&copy; 2025 Bakame AI. Revolutionizing communication through intelligent offline IVR systems.</p>
        </div>
      </footer>
    </div>
  );
};

export default CareersLayout;
