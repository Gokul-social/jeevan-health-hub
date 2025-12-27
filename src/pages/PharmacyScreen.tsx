import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { PageHeader } from "@/components/ui/page-header";
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";
import { 
  MapPin,
  Navigation,
  Phone,
  Clock,
  Star,
  Search,
  Filter,
  ChevronRight,
  Pill,
  AlertTriangle
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Pharmacy {
  id: number;
  name: string;
  address: string;
  distance: string;
  rating: number;
  isOpen: boolean;
  closingTime: string;
  hasStock: boolean;
  lowStockItems: string[];
}

const pharmacies: Pharmacy[] = [
  {
    id: 1,
    name: "Apollo Pharmacy",
    address: "123 MG Road, Near City Hospital",
    distance: "0.5 km",
    rating: 4.5,
    isOpen: true,
    closingTime: "10:00 PM",
    hasStock: true,
    lowStockItems: [],
  },
  {
    id: 2,
    name: "MedPlus",
    address: "456 Gandhi Nagar, Main Market",
    distance: "1.2 km",
    rating: 4.3,
    isOpen: true,
    closingTime: "9:00 PM",
    hasStock: true,
    lowStockItems: ["Paracetamol 500mg"],
  },
  {
    id: 3,
    name: "Wellness Forever",
    address: "789 Station Road, Block B",
    distance: "2.0 km",
    rating: 4.7,
    isOpen: false,
    closingTime: "Closed",
    hasStock: false,
    lowStockItems: ["Azithromycin", "Vitamin D3"],
  },
];

const regions = ["All", "Within 1 km", "Within 2 km", "Within 5 km"];

export default function PharmacyScreen() {
  const [selectedRegion, setSelectedRegion] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <AppLayout>
      <PageHeader
        title="Nearby Pharmacies"
        subtitle="Find medicines near you"
        showBack
      />

      <div className="px-4 py-4 space-y-4">
        {/* Map placeholder */}
        <div className="relative h-48 rounded-2xl bg-secondary overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <MapPin className="w-12 h-12 text-primary mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">Map view coming soon</p>
            </div>
          </div>
          {/* Mock markers */}
          <div className="absolute top-1/3 left-1/4 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-primary-foreground" />
          </div>
          <div className="absolute top-1/2 left-1/2 w-8 h-8 rounded-full bg-success flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-success-foreground" />
          </div>
          <div className="absolute bottom-1/3 right-1/4 w-8 h-8 rounded-full bg-offline flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-offline-foreground" />
          </div>
        </div>

        {/* Search and filter */}
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search medicines..."
              className="w-full h-12 pl-12 pr-4 rounded-xl bg-secondary border-0 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <button className="w-12 h-12 rounded-xl bg-secondary flex items-center justify-center tap-target">
            <Filter className="w-5 h-5 text-muted-foreground" />
          </button>
        </div>

        {/* Region filter */}
        <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
          {regions.map((region) => (
            <button
              key={region}
              onClick={() => setSelectedRegion(region)}
              className={cn(
                "px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all tap-target",
                selectedRegion === region
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              )}
            >
              {region}
            </button>
          ))}
        </div>

        {/* Pharmacy list */}
        <div className="space-y-3">
          {pharmacies.map((pharmacy) => (
            <div
              key={pharmacy.id}
              className={cn(
                "bg-card rounded-2xl p-4 border shadow-sm",
                pharmacy.isOpen ? "border-border/50" : "border-border/30 opacity-75"
              )}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-foreground">{pharmacy.name}</h3>
                    {pharmacy.isOpen ? (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-success-light text-success font-medium">
                        Open
                      </span>
                    ) : (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-destructive-light text-destructive font-medium">
                        Closed
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">{pharmacy.address}</p>
                </div>
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 text-warning fill-warning" />
                  <span className="text-sm font-medium">{pharmacy.rating}</span>
                </div>
              </div>

              <div className="flex items-center gap-4 mb-3">
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Navigation className="w-4 h-4" />
                  {pharmacy.distance}
                </div>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  {pharmacy.closingTime}
                </div>
              </div>

              {/* Low stock warning */}
              {pharmacy.lowStockItems.length > 0 && (
                <div className="flex items-center gap-2 p-3 bg-warning-light rounded-xl mb-3">
                  <AlertTriangle className="w-4 h-4 text-warning flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-warning font-medium">Low stock</p>
                    <p className="text-xs text-muted-foreground truncate">
                      {pharmacy.lowStockItems.join(", ")}
                    </p>
                  </div>
                </div>
              )}

              {/* Medicine availability chips */}
              <div className="flex flex-wrap gap-2 mb-3">
                <span className="px-3 py-1 rounded-full bg-success-light text-success text-xs font-medium flex items-center gap-1">
                  <Pill className="w-3 h-3" />
                  Paracetamol
                </span>
                <span className="px-3 py-1 rounded-full bg-success-light text-success text-xs font-medium flex items-center gap-1">
                  <Pill className="w-3 h-3" />
                  Ibuprofen
                </span>
                <span className="px-3 py-1 rounded-full bg-warning-light text-warning text-xs font-medium flex items-center gap-1">
                  <Pill className="w-3 h-3" />
                  Azithromycin
                </span>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="flex-1 rounded-xl">
                  <Phone className="w-4 h-4 mr-2" />
                  Call
                </Button>
                <Button size="sm" className="flex-1 rounded-xl">
                  <Navigation className="w-4 h-4 mr-2" />
                  Directions
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
