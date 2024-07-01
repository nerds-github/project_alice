import { Theme } from '@mui/material/styles';
import { makeStyles } from '@mui/styles';

const useStyles = makeStyles((theme: Theme) => ({
  chatContainer: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    padding: theme.spacing(2),
  },
  messagesContainer: {
    flexGrow: 1,
    overflowY: 'auto',
    marginBottom: theme.spacing(2),
  },
  actionButtonContainer: {
    display: 'flex',
    justifyContent: 'center',
  },
  right_circle: {
    marginLeft: 'auto !important',
  }
}));

export default useStyles;