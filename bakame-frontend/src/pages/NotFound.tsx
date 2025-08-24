import { Link } from 'react-router-dom';
import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { Home, ArrowLeft, Settings, Phone } from 'lucide-react';
import { Button } from '@/components/ui/button';

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="text-center max-w-md mx-auto">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-muted-foreground/20">404</h1>
          <h2 className="text-2xl font-bold text-foreground mb-2">Page Not Found</h2>
          <p className="text-muted-foreground">
            This page doesn't exist. Access the admin dashboard or IVR interface instead.
          </p>
        </div>
        
        <div className="space-y-4">
          <Link to="/admin-dashboard">
            <Button className="w-full">
              <Settings className="mr-2 h-4 w-4" />
              Admin Dashboard
            </Button>
          </Link>
          
          <Link to="/ivr">
            <Button variant="outline" className="w-full">
              <Phone className="mr-2 h-4 w-4" />
              IVR Interface
            </Button>
          </Link>
          
          <Link to="/" className="inline-flex items-center text-muted-foreground hover:text-foreground">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
