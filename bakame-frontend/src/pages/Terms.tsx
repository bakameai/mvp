
const Terms = () => {
  const sections = [
    {
      title: "Service Description",
      content: [
        "Bakame AI provides Interactive Voice Response (IVR) systems and AI-powered communication solutions.",
        "Our services include offline-capable voice systems, English language education tools, and Kinyarwanda language processing capabilities.",
        "We offer solutions tailored for educational institutions, enterprises, and government organizations.",
        "Services may include software licensing, technical support, training, and custom deployment assistance."
      ]
    },
    {
      title: "User Responsibilities", 
      content: [
        "You must provide accurate information when registering for our services or contacting us.",
        "You are responsible for maintaining the confidentiality of any account credentials provided to you.",
        "You agree to use our services only for lawful purposes and in accordance with these terms.",
        "You must not attempt to reverse engineer, modify, or distribute our proprietary software without permission.",
        "For dataset contribution, you confirm that you have the right to provide voice recordings and consent to their use."
      ]
    },
    {
      title: "Intellectual Property",
      content: [
        "Bakame AI retains all rights to our proprietary technology, software, and AI models.",
        "Voice data contributed to our Kinyarwanda dataset project becomes part of our research corpus under the terms agreed upon during contribution.",
        "Users retain rights to their own content but grant us necessary licenses to provide our services.",
        "Our trademarks, including 'Bakame AI', are our exclusive property.",
        "Open-source components used in our services are governed by their respective licenses."
      ]
    },
    {
      title: "Service Availability",
      content: [
        "We strive to maintain high service availability but cannot guarantee uninterrupted access.",
        "Scheduled maintenance will be communicated in advance when possible.",
        "Our offline-capable IVR systems are designed to function without internet connectivity once deployed.",
        "Service levels for enterprise and government clients are detailed in separate Service Level Agreements (SLAs)."
      ]
    },
    {
      title: "Data Usage and Privacy",
      content: [
        "Your use of our services is also governed by our Privacy Policy.",
        "We process voice data and personal information as described in our Privacy Policy.",
        "For enterprise and government deployments, additional data processing agreements may apply.",
        "You consent to the processing of your data as necessary to provide our services."
      ]
    },
    {
      title: "Payment and Billing",
      content: [
        "Pricing for our services is provided during consultation or as published on our website.",
        "Payment terms are specified in individual service agreements or invoices.",
        "Educational institutions may be eligible for special pricing programs.",
        "Refund policies are detailed in specific service agreements."
      ]
    },
    {
      title: "Limitation of Liability",
      content: [
        "Our liability is limited to the maximum extent permitted by applicable law.",
        "We are not liable for indirect, incidental, or consequential damages arising from your use of our services.",
        "Our total liability for any claim shall not exceed the amount paid by you for the specific service in question.",
        "We do not warrant that our services will meet all of your specific requirements or be error-free.",
        "For government and enterprise clients, liability terms may be modified in separate agreements."
      ]
    },
    {
      title: "Indemnification",
      content: [
        "You agree to indemnify and hold harmless Bakame AI from claims arising from your use of our services.",
        "This includes claims related to your violation of these terms or applicable laws.",
        "You are responsible for ensuring that your use of our services complies with all applicable regulations in your jurisdiction."
      ]
    },
    {
      title: "Termination",
      content: [
        "Either party may terminate service agreements with appropriate notice as specified in individual contracts.",
        "We reserve the right to suspend or terminate access to our services for violations of these terms.",
        "Upon termination, your access to our services will cease, but data retention policies outlined in our Privacy Policy will continue to apply.",
        "Termination does not relieve you of payment obligations for services already provided."
      ]
    },
    {
      title: "Governing Law",
      content: [
        "These terms are governed by the laws of the jurisdiction where Bakame AI is incorporated.",
        "Disputes will be resolved through binding arbitration or in the courts of our jurisdiction.",
        "For international clients, specific jurisdictional agreements may be established in separate contracts."
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 md:p-8 border-b border-border">
        <a href="/" className="text-2xl font-bold">Bakame Ai</a>
        <div className="hidden md:flex space-x-8">
          <a href="/ivr" className="text-muted-foreground hover:text-foreground transition-colors">IVR Demo</a>
          <a href="/blog" className="text-muted-foreground hover:text-foreground transition-colors">Blog</a>
          <a href="/support" className="text-muted-foreground hover:text-foreground transition-colors">Support</a>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-12 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-orange-400 to-blue-400 bg-clip-text text-transparent">
            Terms of Service
          </h1>
          <p className="text-lg text-muted-foreground">
            Effective Date: 2025
          </p>
          <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
            These Terms of Service govern your use of Bakame AI's services, including our IVR systems, 
            AI education tools, and related technologies.
          </p>
        </div>

        {/* Acceptance Notice */}
        <div className="mb-12 p-6 bg-accent/10 backdrop-blur-sm rounded-lg border border-accent/20">
          <h2 className="text-xl font-bold text-foreground mb-3">Agreement to Terms</h2>
          <p className="text-muted-foreground leading-relaxed">
            By accessing or using Bakame AI's services, you agree to be bound by these Terms of Service and our Privacy Policy. 
            If you do not agree to these terms, please do not use our services. These terms apply to all users, 
            including individuals, educational institutions, enterprises, and government organizations.
          </p>
        </div>

        {/* Terms Sections */}
        <div className="space-y-8">
          {sections.map((section, index) => (
            <div key={index} className="bg-card/20 backdrop-blur-sm rounded-lg border border-border p-6">
              <h2 className="text-2xl font-bold text-foreground mb-4">{section.title}</h2>
              <ul className="space-y-3">
                {section.content.map((item, itemIndex) => (
                  <li key={itemIndex} className="text-muted-foreground leading-relaxed">
                    • {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Contact Information */}
        <div className="mt-12 p-6 bg-gradient-to-r from-primary/10 via-accent/10 to-primary/10 rounded-lg border border-accent/20">
          <h2 className="text-2xl font-bold text-foreground mb-4">Questions About These Terms</h2>
          <p className="text-muted-foreground mb-4">
            If you have questions about these Terms of Service or need clarification on any provisions, please contact us:
          </p>
          <div className="space-y-2 text-muted-foreground">
            <p><strong>Email:</strong> happy@bakame.org</p>
            <p><strong>Subject Line:</strong> Terms of Service Inquiry</p>
            <p><strong>Business Hours:</strong> Monday - Friday, 9 AM - 5 PM (CDT)</p>
          </div>
        </div>

        {/* Updates Notice */}
        <div className="mt-8 p-4 bg-secondary/10 rounded-lg border border-secondary/20">
          <p className="text-sm text-muted-foreground">
            <strong>Terms Updates:</strong> We may modify these Terms of Service from time to time. 
            Material changes will be communicated via email or prominent website notice at least 30 days before taking effect. 
            Your continued use of our services after such modifications constitutes acceptance of the updated terms.
          </p>
        </div>

        {/* Severability Notice */}
        <div className="mt-4 p-4 bg-muted/5 rounded-lg border border-muted/20">
          <p className="text-sm text-muted-foreground">
            <strong>Severability:</strong> If any provision of these terms is found to be unenforceable, 
            the remaining provisions will continue to be valid and enforceable to the fullest extent permitted by law.
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border mt-16 p-6">
        <div className="container mx-auto text-center">
          <p className="text-muted-foreground text-sm">
            © 2025 Bakame AI. All rights reserved. | 
            <a href="/support" className="hover:text-foreground ml-1">Support</a> | 
            <a href="/privacy" className="hover:text-foreground ml-1">Privacy</a>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Terms;
