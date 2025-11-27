import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  typography: {
    fontFamily: [
        'Poppins, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    ].join(','),
  },
});

export default theme;