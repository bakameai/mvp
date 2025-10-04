import { useNavigate } from "react-router-dom";
import { ArrowLeft, Target, Eye, Heart, Users, Globe, Shield, Zap } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
const About = () => {
  const navigate = useNavigate();
  return <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 md:p-8 border-b border-border">
        <div className="flex items-center space-x-4">
          <button onClick={() => navigate('/')} className="p-2 hover:bg-muted rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="text-2xl font-bold">Bakame AI</div>
        </div>
        <div className="hidden md:flex space-x-8">
          
          <button onClick={() => navigate('/ivr')} className="text-muted-foreground hover:text-foreground transition-colors">Demo</button>
          <button onClick={() => navigate('/team')} className="text-muted-foreground hover:text-foreground transition-colors">Team</button>
          <button onClick={() => navigate('/contact')} className="text-muted-foreground hover:text-foreground transition-colors">Contact</button>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-20">
        {/* Hero Section */}
        <section className="text-center mb-20">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">About Bakame AI</h1>
          <p className="text-xl md:text-2xl text-muted-foreground max-w-4xl mx-auto">
            We're revolutionizing communication by making AI accessible everywhere, 
            even without internet connectivity. Our mission is to bridge the digital divide 
            and ensure that advanced AI technology works for everyone, everywhere.
          </p>
        </section>

        {/* Our Story */}
        <section className="mb-20">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-8 text-center">Our Story</h2>
            <div className="prose prose-lg max-w-none">
              <p className="text-muted-foreground text-lg mb-6">Founded in 2025, Bakame AI emerged from a simple yet powerful observation: billions of people worldwide lack reliable internet access, yet they deserve the same advanced AI capabilities available in connected urban centers.</p>
              <p className="text-muted-foreground text-lg mb-6">
                Our founders, having experienced firsthand the communication challenges in 
                rural Africa, recognized that traditional cloud-based AI solutions weren't 
                sufficient for truly global accessibility. This led to the development of 
                our groundbreaking offline AI technology.
              </p>
              <p className="text-muted-foreground text-lg">Today, Bakame AI intends to serves thousands of organizations worldwide, from government agencies managing emergency communications to schools providing AI-powered education in remote areas. We're proud to be making AI truly universal.</p>
            </div>
          </div>
        </section>

        {/* Mission, Vision, Values */}
        <section className="mb-20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <Card className="bg-card border-border text-center">
              <CardContent className="p-8">
                <Target className="w-12 h-12 text-primary mx-auto mb-4" />
                <h3 className="text-2xl font-bold mb-4">Our Mission</h3>
                <p className="text-muted-foreground">
                  To democratize AI technology by making it accessible everywhere, 
                  regardless of internet connectivity or geographic location.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card border-border text-center">
              <CardContent className="p-8">
                <Eye className="w-12 h-12 text-accent mx-auto mb-4" />
                <h3 className="text-2xl font-bold mb-4">Our Vision</h3>
                <p className="text-muted-foreground">
                  A world where advanced AI capabilities are available to everyone, 
                  creating equal opportunities for communication and innovation.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card border-border text-center">
              <CardContent className="p-8">
                <Heart className="w-12 h-12 text-secondary mx-auto mb-4" />
                <h3 className="text-2xl font-bold mb-4">Our Values</h3>
                <p className="text-muted-foreground">
                  Inclusivity, innovation, and impact. We believe technology should 
                  serve humanity, not the other way around.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* What Makes Us Different */}
        <section className="mb-20">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center">What Makes Us Different</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="flex items-start space-x-4">
                <Globe className="w-8 h-8 text-accent mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-xl font-bold mb-2">Offline-First Technology</h3>
                  <p className="text-muted-foreground">
                    Our AI works completely offline, ensuring communication never stops, 
                    even in the most remote locations or during network outages.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <Shield className="w-8 h-8 text-primary mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-xl font-bold mb-2">Privacy by Design</h3>
                  <p className="text-muted-foreground">
                    Your data never leaves your premises. Local processing ensures 
                    ultimate privacy and security for sensitive communications.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <Users className="w-8 h-8 text-secondary mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-xl font-bold mb-2">Cultural Sensitivity</h3>
                  <p className="text-muted-foreground">
                    Built with African languages and contexts in mind, our AI 
                    understands cultural nuances and local communication patterns.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <Zap className="w-8 h-8 text-accent mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-xl font-bold mb-2">Lightning Performance</h3>
                  <p className="text-muted-foreground">
                    Local processing means instant responses without the latency 
                    and bandwidth limitations of cloud-based solutions.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Impact Numbers */}
        <section className="mb-20">
          
        </section>

        {/* CTA Section */}
        <section className="text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Transform Your Communication?</h2>
            <p className="text-muted-foreground text-lg mb-8">
              Join thousands of organizations worldwide who trust Bakame AI for their 
              critical communication needs.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button onClick={() => navigate('/contact')} className="bg-primary hover:opacity-90 text-primary-foreground px-8 py-3 text-lg">
                Get Started Today
              </Button>
              <Button onClick={() => navigate('/ivr')} variant="outline" className="border-border text-foreground hover:bg-muted px-8 py-3 text-lg">
                Try Our Demo
              </Button>
            </div>
          </div>
        </section>
      </div>
    </div>;
};
export default About;