import LocalFireDepartmentIcon from "@mui/icons-material/LocalFireDepartment";
import SevereColdIcon from "@mui/icons-material/SevereCold";

export const popularityRatings: Record<string, React.ReactNode> = {
  high: <LocalFireDepartmentIcon className="text-red-500" />,
  medium: <LocalFireDepartmentIcon className="text-yellow-500" />,
  low: <SevereColdIcon className="text-blue-500" />,
};
