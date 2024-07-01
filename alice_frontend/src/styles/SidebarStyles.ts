import { Theme } from '@mui/material/styles';
import { makeStyles } from '@mui/styles';

const useStyles = makeStyles((theme: Theme) => ({
  sidebar: {
    display: 'flex',
    height: '100%',
    backgroundColor: theme.palette.background.paper,
    transition: 'width 0.3s ease',
  },
  content: {
    flexGrow: 1,
    overflowY: 'auto',
    overflowX: 'hidden',
  },
}));

export default useStyles;