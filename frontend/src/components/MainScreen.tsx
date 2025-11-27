import * as React from 'react';
import { useState } from "react";
import { styled, useTheme, type Theme, type CSSObject} from '@mui/material/styles';
import Box from '@mui/material/Box';
import MuiDrawer from '@mui/material/Drawer';
import MuiAppBar from '@mui/material/AppBar';
import AppBarProps from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import CssBaseline from '@mui/material/CssBaseline';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import PersonIcon from '@mui/icons-material/Person';
import ChatBubbleIcon from '@mui/icons-material/ChatBubble';
import AddIcon from '@mui/icons-material/Add';
import ChatContainer from "./ChatContainer"
import type { MainScreenInputs } from "../types/index";

const drawerWidth = 360;

const openedMixin = (theme: Theme): CSSObject => ({
  width: drawerWidth,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: 'hidden',
});

const closedMixin = (theme: Theme): CSSObject => ({
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: 'hidden',
  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up('sm')]: {
    width: `calc(${theme.spacing(8)} + 1px)`,
  },
});

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
}));

interface AppBarProps{
    open?: boolean;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})<AppBarProps>(({ theme }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  variants: [
    {
      props: ({ open }) => open,
      style: {
        marginLeft: drawerWidth,
        width: `calc(100% - ${drawerWidth}px)`,
        transition: theme.transitions.create(['width', 'margin'], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
      },
    },
  ],
}));

const Drawer = styled(MuiDrawer, { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme }) => ({
    width: drawerWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
    boxSizing: 'border-box',
    variants: [
      {
        props: ({ open }) => open,
        style: {
          ...openedMixin(theme),
          '& .MuiDrawer-paper': openedMixin(theme),
        },
      },
      {
        props: ({ open }) => !open,
        style: {
          ...closedMixin(theme),
          '& .MuiDrawer-paper': closedMixin(theme),
        },
      },
    ],
  }),
);

const MainScreen: React.FC<MainScreenInputs> = ({user, pipeline, listOfPipelines}) => {
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const [isGeneralChat, setIsGeneralChat] = useState<boolean>(pipeline.pipeline_name === "general");

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  return (
    <div>
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" open={open}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            sx={[
              {
                marginRight: 5,
              },
              open && { display: 'none' },
            ]}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            {isGeneralChat ? "General Chat" : pipeline.pipeline_name}
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer variant="permanent" open={open}>
      <DrawerHeader
        sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between', 
            px: 2,
        }}
        >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <img 
                src="/src/assets/hoosStudyingBot.svg"
                alt="HoosStudying Logo"
                style={{
                    height: '2em',       
                    width: 'auto',   
                    verticalAlign: 'middle',
                }}
            />
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                HoosStudying
            </Typography>
        </Box>
        
        <IconButton onClick={handleDrawerClose}>
            {theme.direction === 'rtl' ? <ChevronRightIcon /> : <ChevronLeftIcon />}
        </IconButton>
        </DrawerHeader>

        <Divider />
        <List>
            <ListItem disablePadding sx={{ display: 'block' }}>
                <ListItemButton
                sx={{
                    minHeight: 48,
                    px: 2.5,
                    justifyContent: open ? 'initial' : 'center',
                }}
                >
                <ListItemIcon sx={{ minWidth: 0, justifyContent: 'center', mr: open ? 3 : 'auto' }}>
                    <PersonIcon />
                </ListItemIcon>
                <ListItemText
                    primary={`${user.first_name} ${user.last_name}`}
                    secondary={user.email} 
                    sx={{
                        opacity: open ? 1 : 0,
                        '& .MuiListItemText-secondary': {
                        fontSize: '0.8rem',   
                        color: 'text.secondary',
                        },
                    }}
                />
                </ListItemButton>
            </ListItem>

            {!isGeneralChat && (
                <ListItem disablePadding sx={{ display: 'block' }}>
                <ListItemButton
                    sx={{
                    minHeight: 48,
                    px: 2.5,
                    justifyContent: open ? 'initial' : 'center',
                    }}
                    onClick={() => {
                    }}
                >
                    <ListItemIcon sx={{ minWidth: 0, justifyContent: 'center', mr: open ? 3 : 'auto' }}>
                    <ChatBubbleIcon />
                    </ListItemIcon>
                    <ListItemText primary="General Chat" sx={{ opacity: open ? 1 : 0 }} />
                </ListItemButton>
                </ListItem>
            )}
            </List>
        <Divider />
        <Typography
            variant="subtitle2"
            sx={{ px: 2, pt: 2, pb: 1, opacity: open ? 1 : 0, fontWeight: 600, display: "flex",alignItems: 'center', justifyContent: "space-between" }}
            >
            Pipelines
            <IconButton aria-label="Create a new pipeline">
                <AddIcon />
            </IconButton>
        </Typography>
        <List>
        {listOfPipelines.map((p) => (
            <ListItem key={p.pipeline_id} disablePadding sx={{ display: 'block' }}>
            <ListItemButton
                sx={{
                    minHeight: 48,
                    px: 2.5,
                    justifyContent: open ? 'initial' : 'center',
                }}
                onClick={() => {
                    // Here is where we handle switching to this pipeline
                }}
            >
                <ListItemIcon sx={{ minWidth: 0, justifyContent: 'center', mr: open ? 3 : 'auto' }}>
                <   ChatBubbleIcon />
                </ListItemIcon>
                <ListItemText primary={p.pipeline_name} sx={{ opacity: open ? 1 : 0 }} />
            </ListItemButton>
            </ListItem>
        ))}
        </List>


      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <DrawerHeader />
        <ChatContainer user={user}/>
      </Box>
    </Box>
    </div>
  );
}

export default MainScreen