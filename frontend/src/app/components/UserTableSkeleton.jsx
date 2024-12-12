export function SkeletonTable() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-300 rounded mb-4"></div>
      <div className="space-y-4">
        {[...Array(5)].map((_, index) => (
          <div key={index} className="h-6 bg-gray-300 rounded"></div>
        ))}
      </div>
    </div>
  );
}
