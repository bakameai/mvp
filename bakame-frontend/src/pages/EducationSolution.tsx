import { useNavigate } from "react-router-dom";
import { ArrowLeft, Users, Wifi, WifiOff, Play, CheckCircle, TrendingUp } from "lucide-react";
import { useState, useEffect } from "react";
const EducationSolution = () => {
  const navigate = useNavigate();
  const [activeCard, setActiveCard] = useState(0);

  // Auto-rotate feature cards
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveCard(prev => (prev + 1) % 3);
    }, 4000);
    return () => clearInterval(interval);
  }, []);
  return <div className="min-h-screen bg-background text-foreground overflow-hidden">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 md:p-8 border-b border-border backdrop-blur-sm sticky top-0 z-50">
        <div className="flex items-center space-x-4">
          <button onClick={() => navigate('/')} className="p-2 hover:bg-muted rounded-lg transition-all duration-300 hover:scale-105">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="text-2xl font-bold">Bakame Ai</div>
        </div>
        <div className="hidden md:flex space-x-8">
          <a href="/blog" className="text-muted-foreground hover:text-foreground transition-colors hover:scale-105 transform duration-200">Blog</a>
          
        </div>
      </nav>

      <div className="container mx-auto px-6 py-20">
        {/* Hero Section */}
        <div className="text-center mb-16 relative">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent animate-fade-in">
            Education Solutions
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto animate-fade-in">
            Empowering educational institutions with offline-first IVR systems that work in any environment, from remote villages to urban campuses.
          </p>
        </div>

        {/* Interactive How It Works Section */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold mb-12 text-center">How Bakame AI Works for Education</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[{
            icon: WifiOff,
            title: "Offline-First Design",
            description: "Works completely offline, perfect for schools in remote areas with limited internet connectivity. All processing happens locally on the device.",
            color: "blue"
          }, {
            icon: Users,
            title: "Multi-Language Support",
            description: "Built-in support for Kinyarwanda, English, French, and Swahili, making education accessible to students in their native languages.",
            color: "purple"
          }, {
            icon: Play,
            title: "Interactive Learning",
            description: "Students can access course materials, submit assignments, and receive feedback through voice interactions, even without smartphones.",
            color: "green"
          }].map((feature, index) => <div key={index} className={`bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 transition-all duration-500 hover:scale-105 hover:bg-white/10 cursor-pointer ${activeCard === index ? 'ring-2 ring-blue-400/50 scale-105' : ''}`} onMouseEnter={() => setActiveCard(index)}>
                <div className={`w-12 h-12 bg-${feature.color}-500/20 rounded-lg flex items-center justify-center mb-4 transition-all duration-300`}>
                  <feature.icon className={`w-6 h-6 text-${feature.color}-400`} />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
                <div className="mt-4 w-full bg-white/10 rounded-full h-1">
                  <div className={`h-1 bg-${feature.color}-400 rounded-full transition-all duration-1000 ${activeCard === index ? 'w-full' : 'w-0'}`}></div>
                </div>
              </div>)}
          </div>
        </div>

        {/* Enhanced Use Cases Section */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold mb-12 text-center">Educational Use Cases</h2>
          <div className="space-y-8">
            {[{
            title: "Remote Learning Support",
            description: "Students in rural areas can access lectures, participate in discussions, and complete assignments using basic phones. The system works entirely offline, storing content locally and syncing when connectivity is available.",
            features: ["Voice-based course delivery", "Assignment submission via voice", "Progress tracking without internet"],
            color: "blue",
            icon: Play
          }, {
            title: "Language Learning",
            description: "Interactive language learning programs that help students practice pronunciation, vocabulary, and conversation skills in multiple languages, with AI-powered feedback and corrections.",
            features: ["Pronunciation practice and correction", "Vocabulary building exercises", "Conversational AI tutoring"],
            color: "purple",
            icon: Users
          }, {
            title: "Administrative Services",
            description: "Automated systems for student enrollment, grade inquiries, schedule information, and parent-teacher communication, all accessible through simple phone calls.",
            features: ["Student information systems", "Grade and attendance queries", "Parent communication portal"],
            color: "green",
            icon: CheckCircle
          }].map((useCase, index) => <div key={index} className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10 hover:bg-white/10 transition-all duration-500 group">
                <div className="flex items-start space-x-4">
                  <div className={`w-12 h-12 bg-${useCase.color}-500/20 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                    <useCase.icon className={`w-6 h-6 text-${useCase.color}-400`} />
                  </div>
                  <div className="flex-1">
                    <h3 className={`text-2xl font-semibold mb-4 text-${useCase.color}-400`}>{useCase.title}</h3>
                    <p className="text-muted-foreground mb-4">{useCase.description}</p>
                    <ul className="list-disc list-inside text-muted-foreground space-y-2">
                      {useCase.features.map((feature, featureIndex) => <li key={featureIndex} className="flex items-center space-x-2">
                          <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                          <span>{feature}</span>
                        </li>)}
                    </ul>
                  </div>
                </div>
              </div>)}
          </div>
        </div>

        {/* Enhanced Benefits Section - Card Design */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold mb-12 text-center">Key Benefits</h2>
          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10 hover:bg-white/10 transition-all duration-300 group">
              <h3 className="text-2xl font-semibold mb-6 text-blue-400 flex items-center group">
                <TrendingUp className="w-6 h-6 mr-3 group-hover:scale-110 transition-transform duration-300" />
                For Students
              </h3>
              <div className="space-y-4">
                {["Access education from anywhere, even without internet", "Learn in their native language", "No need for expensive devices or data plans", "Personalized learning experiences"].map((benefit, index) => <div key={index} className={`bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-all duration-300 delay-${index * 100} hover:scale-105`}>
                    <span className="text-foreground leading-relaxed">{benefit}</span>
                  </div>)}
              </div>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10 hover:bg-white/10 transition-all duration-300 group">
              <h3 className="text-2xl font-semibold mb-6 text-purple-400 flex items-center group">
                <Users className="w-6 h-6 mr-3 group-hover:scale-110 transition-transform duration-300" />
                For Institutions
              </h3>
              <div className="space-y-4">
                {["Reach students in remote areas", "Reduce infrastructure costs", "Automate administrative tasks", "Improve student engagement and retention"].map((benefit, index) => <div key={index} className={`bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-all duration-300 delay-${index * 100} hover:scale-105`}>
                    <span className="text-foreground leading-relaxed">{benefit}</span>
                  </div>)}
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced CTA Section */}
        <div className="text-center bg-gradient-to-r from-white/5 to-white/10 backdrop-blur-sm rounded-3xl p-12 border border-white/10 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 animate-pulse"></div>
          <div className="relative z-10">
            <h2 className="text-3xl font-bold mb-6">Ready to Transform Education?</h2>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Join schools and universities already using Bakame AI to provide accessible, offline education to their students.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button onClick={() => navigate('/signup')} className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-8 py-4 rounded-full font-semibold text-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/25">
                Get Started Today
              </button>
              <button className="border border-border text-foreground px-8 py-4 rounded-full font-semibold text-lg hover:bg-muted transition-all duration-300 hover:scale-105 hover:border-muted-foreground">
                Schedule Demo
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>;
};
export default EducationSolution;