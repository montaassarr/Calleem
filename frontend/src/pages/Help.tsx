import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Book, MessageCircle, FileText, Video, ExternalLink } from "lucide-react";

const Help = () => {
  const resources = [
    {
      title: "Documentation",
      description: "Complete guide to using the AI Receptionist dashboard",
      icon: Book,
      color: "from-blue-500 to-cyan-500",
      link: "/docs",
    },
    {
      title: "API Reference",
      description: "Backend API endpoints and integration guide",
      icon: FileText,
      color: "from-purple-500 to-pink-500",
      link: "http://localhost:8000/docs",
      external: true,
    },
    {
      title: "Video Tutorials",
      description: "Watch step-by-step guides and tutorials",
      icon: Video,
      color: "from-green-500 to-emerald-500",
      link: "#",
    },
    {
      title: "Support",
      description: "Contact support team for assistance",
      icon: MessageCircle,
      color: "from-orange-500 to-red-500",
      link: "mailto:support@royalfade.com",
      external: true,
    },
  ];

  const faq = [
    {
      question: "How do I test the AI receptionist?",
      answer: "Navigate to AI Receptionist → Test AI Chat to send test messages and see how the AI responds.",
    },
    {
      question: "How do I add new services?",
      answer: "Go to Services page and click 'Add Service' button. Fill in the details and save.",
    },
    {
      question: "Can I export appointment data?",
      answer: "Yes, on the Appointments page, click 'Export Data' button to download CSV or PDF reports.",
    },
    {
      question: "How do I configure Twilio webhooks?",
      answer: "Visit the WhatsApp page to get your webhook URLs and follow the setup instructions.",
    },
    {
      question: "How do I add team members?",
      answer: "Go to Settings → Team Members and click 'Add User' to create new dashboard accounts.",
    },
  ];

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold mb-2">Help & Support</h1>
            <p className="text-muted-foreground">
              Find answers, guides, and resources
            </p>
          </div>

          {/* Resources Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {resources.map((resource) => (
              <a
                key={resource.title}
                href={resource.link}
                target={resource.external ? "_blank" : "_self"}
                rel={resource.external ? "noopener noreferrer" : ""}
                className="glass rounded-2xl p-6 hover:shadow-lg transition-all group"
              >
                <div className="flex items-start gap-4">
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${resource.color} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                    <resource.icon className="w-7 h-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-lg font-semibold">{resource.title}</h3>
                      {resource.external && <ExternalLink className="w-4 h-4" />}
                    </div>
                    <p className="text-sm text-muted-foreground">{resource.description}</p>
                  </div>
                </div>
              </a>
            ))}
          </div>

          {/* FAQ */}
          <div className="glass rounded-2xl p-6">
            <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
            <div className="space-y-6">
              {faq.map((item, index) => (
                <div key={index} className="pb-6 border-b border-white/10 last:border-0">
                  <h3 className="text-lg font-semibold mb-2">{item.question}</h3>
                  <p className="text-muted-foreground">{item.answer}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div className="mt-6 glass rounded-2xl p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline">
                → API Documentation
              </a>
              <a href="/settings" className="text-sm text-primary hover:underline">
                → Settings
              </a>
              <a href="/ai-receptionist/test" className="text-sm text-primary hover:underline">
                → Test AI Chat
              </a>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Help;
