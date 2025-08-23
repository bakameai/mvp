
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface StatusSelectorProps {
  status: string | null;
  onStatusChange: (value: string) => void;
  disabled?: boolean;
}

export const StatusSelector = ({ status, onStatusChange, disabled }: StatusSelectorProps) => {
  return (
    <Select
      value={status || 'new'}
      onValueChange={onStatusChange}
      disabled={disabled}
    >
      <SelectTrigger className="w-40">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="new">New</SelectItem>
        <SelectItem value="in_progress">In Progress</SelectItem>
        <SelectItem value="resolved">Resolved</SelectItem>
        <SelectItem value="closed">Closed</SelectItem>
      </SelectContent>
    </Select>
  );
};
