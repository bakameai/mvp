import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { MapPin, Clock, ArrowRight } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import ApplicationForm from "./ApplicationForm";

interface JobListingsProps {
  onApply: (jobTitle: string) => void;
}

const JobListings = ({ onApply }: JobListingsProps) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hoveredJob, setHoveredJob] = useState<number | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const jobListings = [
    {
      title: "Senior AI Engineer",
      team: "Engineering",
      location: "San Francisco, CA",
      type: "Full-time",
      description: "Lead the development of our offline AI communication systems and work with cutting-edge technology to revolutionize how people communicate without traditional infrastructure."
    }, {
      title: "Product Manager - AI Solutions",
      team: "Product",
      location: "New York, NY",
      type: "Full-time",
      description: "Drive product strategy for our innovative offline IVR systems. Shape the future of communication technology and make it accessible to everyone, everywhere."
    }, {
      title: "Machine Learning Research Scientist",
      team: "Research",
      location: "Remote",
      type: "Full-time",
      description: "Conduct groundbreaking research in offline AI communication. Publish papers and contribute to the advancement of accessible AI technology."
    }, {
      title: "UX Designer",
      team: "Design",
      location: "Austin, TX",
      type: "Full-time",
      description: "Design intuitive interfaces for complex AI systems. Create user experiences that make advanced technology accessible to users with varying technical backgrounds."
    }, {
      title: "DevOps Engineer",
      team: "Engineering",
      location: "Remote",
      type: "Full-time",
      description: "Build and maintain the infrastructure that powers our AI systems. Ensure scalability, reliability, and security of our offline communication platforms."
    }, {
      title: "AI Research Intern",
      team: "Research",
      location: "Remote",
      type: "Internship",
      description: "Contribute to groundbreaking research in offline AI communication. Perfect for students passionate about AI innovation and social impact."
    }
  ];

  const handleApplyClick = (jobTitle: string) => {
    setSelectedJob(jobTitle);
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedJob("");
  };

  return (
    <>
      <div className={`mb-20 transition-all duration-700 ease-out delay-300 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
        <h2 className="text-3xl font-bold mb-12 text-white">Open roles</h2>
        <div className="space-y-6">
          {jobListings.map((job, index) => (
            <div 
              key={index} 
              className={`border border-gray-700 bg-gray-800/30 rounded-lg p-8 transition-all duration-300 cursor-pointer ${
                hoveredJob === index 
                  ? 'border-blue-500/50 bg-gray-800/50 shadow-lg shadow-blue-500/10 translate-y-[-2px]' 
                  : 'hover:border-gray-600 hover:bg-gray-800/40'
              }`}
              onMouseEnter={() => setHoveredJob(index)}
              onMouseLeave={() => setHoveredJob(null)}
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2 transition-colors duration-200">
                    {job.title}
                  </h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-300">
                    <span className="bg-gray-700/70 px-3 py-1 rounded-full transition-colors duration-200 hover:bg-gray-600">
                      {job.team}
                    </span>
                    <div className="flex items-center">
                      <MapPin className="w-4 h-4 mr-1" />
                      {job.location}
                    </div>
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      {job.type}
                    </div>
                  </div>
                </div>
                <Button 
                  variant="outline" 
                  className={`group border-gray-600 bg-transparent text-white transition-all duration-200 ${
                    hoveredJob === index 
                      ? 'border-blue-500 bg-blue-500/10 text-blue-400' 
                      : 'hover:bg-gray-700 hover:border-gray-500'
                  }`}
                  onClick={() => handleApplyClick(job.title)}
                >
                  Apply
                  <ArrowRight className={`w-4 h-4 ml-2 transition-transform duration-200 ${
                    hoveredJob === index ? 'translate-x-1' : 'group-hover:translate-x-1'
                  }`} />
                </Button>
              </div>
              <p className="text-gray-300 leading-relaxed">{job.description}</p>
            </div>
          ))}
        </div>
      </div>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-700">
          <DialogHeader>
            <DialogTitle className="text-white text-2xl">Apply for {selectedJob}</DialogTitle>
          </DialogHeader>
          <ApplicationForm 
            initialPosition={selectedJob} 
            onSubmit={handleDialogClose}
          />
        </DialogContent>
      </Dialog>
    </>
  );
};

export default JobListings;
