import React, { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Users as UsersIcon, Plus, Edit, Trash2 } from "lucide-react";
import { StatCard } from "@/components/dashboard/StatCard";
import { adminAPI } from "@/services/api";

const Users = () => {
  const [userStats, setUserStats] = useState([
    { title: "Total Students", value: "0", icon: UsersIcon, iconColor: "blue" as const },
    { title: "Active Today", value: "0", icon: UsersIcon, iconColor: "green" as const },
    { title: "New This Week", value: "0", icon: UsersIcon, iconColor: "purple" as const },
    { title: "IVR Sessions", value: "0", icon: UsersIcon, iconColor: "orange" as const },
  ]);

  const [users, setUsers] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [adminStats, ivrStats] = await Promise.all([
          adminAPI.getAdminStats(),
          adminAPI.getIVRStats()
        ]);
        
        setUserStats([
          { title: "Total Students", value: adminStats.total_users?.toString() || "0", icon: UsersIcon, iconColor: "blue" as const },
          { title: "Active Today", value: adminStats.active_users?.toString() || "0", icon: UsersIcon, iconColor: "green" as const },
          { title: "New This Week", value: adminStats.new_users_this_month?.toString() || "0", icon: UsersIcon, iconColor: "purple" as const },
          { title: "IVR Sessions", value: ivrStats.total_ivr_sessions?.toString() || "0", icon: UsersIcon, iconColor: "orange" as const },
        ]);
      } catch (error) {
        console.error('Error fetching user stats:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <DashboardLayout>
      <div className="p-8 space-y-8">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-foreground">IVR Learning Students</h1>
          <Button className="bg-primary hover:bg-primary/90">
            <Plus className="h-4 w-4 mr-2" />
            Add Student
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {userStats.map((stat, index) => (
            <StatCard
              key={index}
              title={stat.title}
              value={stat.value}
              icon={stat.icon}
              iconColor={stat.iconColor}
            />
          ))}
        </div>

        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-border">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-muted-foreground">Phone Number</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-muted-foreground">Sessions</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-muted-foreground">Last Active</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-muted-foreground">Status</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-border">
                    <td className="px-6 py-4 text-sm text-foreground font-medium">+250 XXX XXX XXX</td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">12 sessions</td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">2 hours ago</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 text-xs rounded-full bg-stat-green/10 text-stat-green">
                        Active
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Users;
