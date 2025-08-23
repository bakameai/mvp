import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authAPI } from "@/services/api";
import { SecureAuthForm } from "@/components/auth/SecureAuthForm";
const Signup = () => {
  const navigate = useNavigate();

  // Check if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      const { session } = authAPI.getSession();
      if (session) {
        navigate("/");
      }
    };
    checkAuth();
  }, [navigate]);
  const handleAuthSuccess = (isAdmin: boolean) => {
    // Redirect admin users to dashboard, regular users to home
    if (isAdmin) {
      navigate("/admin-dashboard");
    } else {
      navigate("/");
    }
  };
  return <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Background effects similar to main page */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-radial from-blue-500/8 via-blue-500/4 to-transparent rounded-full blur-2xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-gradient-radial from-purple-500/10 via-purple-500/5 to-transparent rounded-full blur-2xl animate-pulse delay-1000"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-20 flex justify-between items-center p-6 md:p-8">
        <a href="/" className="text-2xl font-bold hover:text-blue-400 transition-colors">
          Bakame Ai
        </a>
        
      </nav>

      {/* Main content */}
      <div className="relative z-10 container mx-auto px-6 py-20">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent">
            Join Bakame AI
          </h1>
          <p className="text-xl text-white/70 max-w-2xl mx-auto">
            Get started with offline IVR intelligence and revolutionary communication solutions
          </p>
        </div>

        <div className="flex justify-center">
          <SecureAuthForm onSuccess={handleAuthSuccess} />
        </div>

        <div className="text-center mt-8">
          <p className="text-white/60">
            Already have an account?{' '}
            <button onClick={() => navigate('/')} className="text-blue-400 hover:text-blue-300 underline">
              Go back to home
            </button>
          </p>
        </div>
      </div>
    </div>;
};
export default Signup;
