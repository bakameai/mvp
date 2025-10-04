
export function getStatusColor(status: string | null) {
  switch (status) {
    case 'new': return 'bg-blue-500';
    case 'in_progress': return 'bg-yellow-500';
    case 'resolved': return 'bg-green-500';
    case 'closed': return 'bg-gray-500';
    default: return 'bg-blue-500';
  }
}

export function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
