import SportsBasketballIcon from "@mui/icons-material/SportsBasketball";
import NewspaperIcon from "@mui/icons-material/Newspaper";
import FlagIcon from "@mui/icons-material/Flag";
import PublicIcon from "@mui/icons-material/Public";
import WorkIcon from "@mui/icons-material/Work";
import GavelIcon from "@mui/icons-material/Gavel";
import OutlinedFlagIcon from "@mui/icons-material/OutlinedFlag";
import ColorLensIcon from "@mui/icons-material/ColorLens";
import LocalHospitalIcon from "@mui/icons-material/LocalHospital";
import DeveloperBoardIcon from "@mui/icons-material/DeveloperBoard";
import RadioIcon from "@mui/icons-material/Radio";
import ScienceIcon from "@mui/icons-material/Science";
import SettingsInputAntennaIcon from "@mui/icons-material/SettingsInputAntenna";
import InfoOutlineIcon from "@mui/icons-material/InfoOutline";

export const categoryIcons: Record<string, React.ReactNode> = {
  sport: <SportsBasketballIcon className="text-gray-700" />,
  news: <NewspaperIcon className="text-gray-700" />,
  uk: <FlagIcon className="text-gray-700" />,
  world: <PublicIcon className="text-gray-700" />,
  business: <WorkIcon className="text-gray-700" />,
  politics: <GavelIcon className="text-gray-700" />,
  us_and_canada: <OutlinedFlagIcon className="text-gray-700" />,
  entertainment_and_arts: <ColorLensIcon className="text-gray-700" />,
  health: <LocalHospitalIcon className="text-gray-700" />,
  technology: <DeveloperBoardIcon className="text-gray-700" />,
  world_radio_and_tv: <RadioIcon className="text-gray-700" />,
  science_and_environment: <ScienceIcon className="text-gray-700" />,
  newsbeat: <SettingsInputAntennaIcon className="text-gray-700" />,
  default: <InfoOutlineIcon className="text-gray-700" />,
};
