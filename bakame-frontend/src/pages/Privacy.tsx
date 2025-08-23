const Privacy = () => {
  const sections = [
    {
      title: "Information We Collect",
      content: [
        "Personal Information: When you contact us, sign up for early access, or use our services, we may collect your name, email address, phone number, and organization details.",
        "Voice Data: When you participate in our IVR demo or contribute to our Kinyarwanda dataset, we collect voice recordings and associated metadata.",
        "Usage Data: We collect information about how you interact with our website and services, including IP addresses, browser information, and usage patterns.",
        "Technical Data: For enterprise and government deployments, we may collect system performance data and error logs to improve our services."
      ]
    },
    {
      title: "How We Use Your Information",
      content: [
        "Service Provision: To provide, maintain, and improve our IVR and AI education services.",
        "Dataset Development: Voice data is used to train and improve our Kinyarwanda language models.",
        "Communication: To respond to your inquiries, provide support, and send important service updates.",
        "Research: To advance AI research for low-resource languages and offline communication technologies.",
        "Legal Compliance: To comply with applicable laws and regulations."
      ]
    },
    {
      title: "Data Sharing and Disclosure",
      content: [
        "We do not sell your personal information to third parties.",
        "Research Partners: Anonymized voice data may be shared with academic research institutions for language research purposes.",
        "Service Providers: We may share data with trusted service providers who assist in delivering our services.",
        "Legal Requirements: We may disclose information when required by law or to protect our rights and safety.",
        "Business Transfers: In the event of a merger or acquisition, user data may be transferred as part of the business assets."
      ]
    },
    {
      title: "Data Security",
      content: [
        "We implement industry-standard security measures to protect your data.",
        "Voice data is encrypted both in transit and at rest.",
        "Access to personal data is restricted to authorized personnel only.",
        "For government and enterprise clients, we provide additional security protocols and compliance certifications.",
        "Regular security audits are conducted to ensure data protection standards."
      ]
    },
    {
      title: "Your Rights",
      content: [
        "Access: You have the right to access the personal information we hold about you.",
        "Correction: You can request correction of inaccurate or incomplete information.",
        "Deletion: You can request deletion of your personal data, subject to legal and operational requirements.",
        "Portability: You can request a copy of your data in a portable format.",
        "Withdrawal: You can withdraw consent for data processing where applicable."
      ]
    },
    {
      title: "International Data Transfers",
      content: [
        "Bakame AI operates globally and may process data in countries other than your own.",
        "We ensure appropriate safeguards are in place for international data transfers.",
        "For users in the European Union, we comply with GDPR requirements for data transfers.",
        "Data localization requirements for government clients are addressed on a case-by-case basis."
      ]
    },
    {
      title: "Retention Period",
      content: [
        "Personal information is retained only as long as necessary for the purposes outlined in this policy.",
        "Voice data for dataset contribution may be retained longer to support ongoing research and model improvement.",
        "You can request deletion of your data at any time, subject to legal obligations.",
        "Anonymized data may be retained indefinitely for research purposes."
      ]
    },
    {
      title: "Children's Privacy",
      content: [
        "Our services are not directed to children under 13 years of age.",
        "For educational deployments involving minors, appropriate consents and safeguards are implemented.",
        "We comply with applicable children's privacy laws in jurisdictions where we operate."
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
            Privacy Policy
          </h1>
          <p className="text-lg text-muted-foreground">
            Effective Date: January 2025
          </p>
          <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
            This Privacy Policy explains how Bakame AI collects, uses, and protects your information when you use our services.
          </p>
        </div>

        {/* Introduction */}
        <div className="mb-12 p-6 bg-card/30 backdrop-blur-sm rounded-lg border border-border">
          <p className="text-muted-foreground leading-relaxed">
            At Bakame AI, we are committed to protecting your privacy and ensuring the security of your personal information. 
            This policy applies to all users of our IVR systems, website visitors, dataset contributors, and clients across 
            our education, enterprise, and government solutions.
          </p>
        </div>

        {/* Policy Sections */}
        <div className="space-y-8">
          {sections.map((section, index) => (
            <div key={index} className="bg-card/20 backdrop-blur-sm rounded-lg border border-border p-6">
              <h2 className="text-2xl font-bold text-white mb-4">{section.title}</h2>
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
        <div className="mt-12 p-6 bg-gradient-to-r from-blue-500/10 via-orange-500/10 to-blue-500/10 rounded-lg border border-accent/20">
          <h2 className="text-2xl font-bold text-white mb-4">Contact Us About Privacy</h2>
          <p className="text-muted-foreground mb-4">
            If you have questions about this Privacy Policy or want to exercise your privacy rights, please contact us:
          </p>
          <div className="space-y-2 text-muted-foreground">
            <p><strong>Email:</strong> happy@bakame.org</p>
            <p><strong>Subject Line:</strong> Privacy Policy Inquiry</p>
            <p><strong>Response Time:</strong> We will respond to privacy inquiries within 72 hours</p>
          </div>
        </div>

        {/* Updates Notice */}
        <div className="mt-8 p-4 bg-secondary/10 rounded-lg border border-secondary/20">
          <p className="text-sm text-muted-foreground">
            <strong>Policy Updates:</strong> We may update this Privacy Policy from time to time. 
            We will notify users of significant changes via email or prominent notice on our website. 
            Your continued use of our services after such modifications constitutes acceptance of the updated policy.
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border mt-16 p-6">
        <div className="container mx-auto text-center">
          <p className="text-muted-foreground text-sm">
            © 2025 Bakame AI. All rights reserved. | 
            <a href="/support" className="hover:text-foreground ml-1">Support</a> | 
            <a href="/terms" className="hover:text-foreground ml-1">Terms</a>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Privacy;
