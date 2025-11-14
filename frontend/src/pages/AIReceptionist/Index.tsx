import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Bot, MessageSquare, Settings, TestTube, TrendingUp, Zap } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { conversationsApi, webhookApi } from "@/api";
import { useNavigate } from "react-router-dom";

const AIReceptionist = () => {
  const navigate = useNavigate();

  const { data: conversations = [] } = useQuery({
    queryKey: ["conversations"],
    queryFn: () => conversationsApi.getRecent(10),
  });

  const { data: webhookStatus } = useQuery({
    queryKey: ["webhook-status"],
    queryFn: () => webhookApi.getStatus(),
  });

  const stats = [
    {
      title: "Total Conversations",
      value: conversations.length.toString(),
      icon: MessageSquare,
      color: "from-blue-500 to-cyan-500",
    },
    {
      title: "Active Now",
      value: conversations.filter((c: any) => c.status === "active").length.toString(),
      icon: Zap,
      color: "from-green-500 to-emerald-500",
    },
    {
      title: "Success Rate",
      value: "94%",
      icon: TrendingUp,
      color: "from-purple-500 to-pink-500",
    },
  ];

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">AI Receptionist</h1>
              <p className="text-muted-foreground">
                Monitor and manage your AI-powered customer service
              </p>
            </div>
            <Button 
              className="gap-2 bg-gradient-to-r from-primary to-accent"
              onClick={() => navigate('/ai-receptionist/test')}
            >
              <TestTube className="w-4 h-4" />
              Test AI Chat
            </Button>
          </div>

          {/* Status Banner */}
          <div className="glass rounded-2xl p-6 mb-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                  <Bot className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-1">AI Status</h3>
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full animate-pulse ${
                      webhookStatus?.status === 'active' ? 'bg-green-400' : 'bg-red-400'
                    }`} />
                    <span className="text-sm text-muted-foreground">
                      {webhookStatus?.status === 'active' ? 'Online & Ready' : 'Offline'}
                    </span>
                  </div>
                </div>
              </div>
              <Button 
                variant="outline" 
                className="gap-2"
                onClick={() => navigate('/settings/ai')}
              >
                <Settings className="w-4 h-4" />
                Configure AI
              </Button>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {stats.map((stat) => (
              <div key={stat.title} className="glass rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center`}>
                    <stat.icon className="w-6 h-6 text-white" />
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mb-1">{stat.title}</p>
                <p className="text-3xl font-bold">{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Test AI */}
            <div 
              className="glass rounded-2xl p-6 hover:shadow-lg transition-all cursor-pointer group"
              onClick={() => navigate('/ai-receptionist/test')}
            >
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <TestTube className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-2">Test AI Chat</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Test your AI receptionist with sample messages and see how it responds
                  </p>
                  <Button variant="ghost" className="gap-2 group-hover:translate-x-1 transition-transform">
                    Open Test Interface →
                  </Button>
                </div>
              </div>
            </div>

            {/* View Conversations */}
            <div 
              className="glass rounded-2xl p-6 hover:shadow-lg transition-all cursor-pointer group"
              onClick={() => navigate('/conversations')}
            >
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-2">Conversation History</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    View all customer interactions and AI responses
                  </p>
                  <Button variant="ghost" className="gap-2 group-hover:translate-x-1 transition-transform">
                    View All Conversations →
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Conversations */}
          <div className="glass rounded-2xl p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Conversations</h3>
            {conversations.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">
                No conversations yet. Start by testing your AI or wait for customer messages.
              </p>
            ) : (
              <div className="space-y-3">
                {conversations.slice(0, 5).map((conv: any) => (
                  <div 
                    key={conv.id} 
                    className="glass-strong rounded-lg p-4 hover:bg-white/10 transition-colors cursor-pointer"
                    onClick={() => navigate(`/conversations/${conv.id}`)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{conv.phone_number}</span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(conv.updated_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-1">
                      {conv.messages[conv.messages.length - 1]?.text || 'No messages'}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                        {conv.state.intent?.replace('_', ' ') || 'unknown'}
                      </span>
                      <span className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                        {conv.messages.length} messages
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default AIReceptionist;
