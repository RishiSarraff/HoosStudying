import * as React from "react";
import { useState } from "react";
import {
  styled,
  useTheme,
  type Theme,
  type CSSObject,
} from "@mui/material/styles";
import Box from "@mui/material/Box";
import MuiDrawer from "@mui/material/Drawer";
import MuiAppBar from "@mui/material/AppBar";
import AppBarProps from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import List from "@mui/material/List";
import CssBaseline from "@mui/material/CssBaseline";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import PersonIcon from "@mui/icons-material/Person";
import ChatBubbleIcon from "@mui/icons-material/ChatBubble";
import AddIcon from "@mui/icons-material/Add";
import GeneralChatContainer from "./GeneralChatContainer";
import {
  type MySQLPipeline,
  type MainScreenInputs,
  type MySQLConversation,
  type MySQLMessage,
} from "../types/index";
import NewPipelineModal from "./NewPipelineModal";
import {
  createNewPipeline,
  deletePipeline,
  getAllNonDefaultPipelines,
  editPipeline,
} from "../services/pipeline";
import {
  getConversations,
  getMessagesForConversation,
} from "../services/conversation";
import { getCurrentToken, logout } from "../services/auth";
import PipelineCard from "./PipelineCard";
import SettingsIcon from "@mui/icons-material/Settings";
import FolderIcon from "@mui/icons-material/Folder";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import CustomAlert from "./CustomAlert";
import FilesButton from "./FilesButton";
import ChatButton from "./ChatButton";
import FilesSearchBar from "./FilesSearchBar";
import UploadFilesButton from "./UploadFilesButton";
import PipelineContainer from "./PipelineContainer";
import EditSquareIcon from "@mui/icons-material/EditSquare";
import ConversationCard from "./ConversationCard";
import ConversationView from "./ConversationView";
import HomeIcon from "@mui/icons-material/Home";

const drawerWidth = 360;

const openedMixin = (theme: Theme): CSSObject => ({
  width: drawerWidth,
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: "hidden",
});

const closedMixin = (theme: Theme): CSSObject => ({
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: "hidden",
  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up("sm")]: {
    width: `calc(${theme.spacing(8)} + 1px)`,
  },
});

const DrawerHeader = styled("div")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "flex-end",
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
}));

interface AppBarProps {
  open?: boolean;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== "open",
})<AppBarProps>(({ theme }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(["width", "margin"], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  variants: [
    {
      props: ({ open }) => open,
      style: {
        marginLeft: drawerWidth,
        width: `calc(100% - ${drawerWidth}px)`,
        transition: theme.transitions.create(["width", "margin"], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
      },
    },
  ],
}));

const Drawer = styled(MuiDrawer, {
  shouldForwardProp: (prop) => prop !== "open",
})(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
  whiteSpace: "nowrap",
  boxSizing: "border-box",
  variants: [
    {
      props: ({ open }) => open,
      style: {
        ...openedMixin(theme),
        "& .MuiDrawer-paper": openedMixin(theme),
      },
    },
    {
      props: ({ open }) => !open,
      style: {
        ...closedMixin(theme),
        "& .MuiDrawer-paper": closedMixin(theme),
      },
    },
  ],
}));

const MainScreen: React.FC<MainScreenInputs> = ({
  user,
  pipeline,
  listOfPipelines: initialPipelines,
}) => {
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const [viewMode, setViewMode] = useState<boolean>(
    pipeline.pipeline_name === "general"
  );
  const [openNewPipelineModal, setOpenNewPipelineModal] =
    useState<boolean>(false);
  const [openDeleteModal, setOpenDeleteModal] = useState<boolean>(false);
  const [pipelineToDelete, setPipelineToDelete] = useState<MySQLPipeline>();
  const [listOfPipelines, setListOfPipelines] =
    useState<MySQLPipeline[]>(initialPipelines);

  React.useEffect(() => {
    setListOfPipelines(initialPipelines);
  }, [initialPipelines]);
  const [alertState, setAlertState] = useState({
    open: false,
    message: "",
    severity: "success" as "success" | "error",
  });
  const [currentPipeline, setCurrentPipeline] =
    useState<MySQLPipeline>(pipeline);
  const [showChat, setShowChat] = useState(true);
  const [refreshDocuments, setRefreshDocuments] = useState<number>(0);
  const [openEditPipelineModal, setOpenEditPipelineModal] =
    useState<boolean>(false);
  const [listOfConversations, setListOfConversations] = useState<
    MySQLConversation[]
  >([]);
  const [currentConversation, setCurrentConversation] =
    useState<MySQLConversation>();
  const [currentMessages, setCurrentMessages] = useState<MySQLMessage[]>();
  const [openGeneralPipelineChatPage, setOpenGeneralPipelineChatPage] =
    useState<boolean>(false);

  const showAlert = (
    message: string,
    severity: "success" | "error" = "success"
  ) => {
    setAlertState({ open: true, message, severity });
  };

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  const refreshPipelines = async () => {
    try {
      const token = await getCurrentToken();
      if (token) {
        const updatedPipelines = await getAllNonDefaultPipelines(token);
        setListOfPipelines(updatedPipelines);
      }
    } catch (error) {
      console.error("Error refreshing pipelines:", error);
    }
  };

  const handleNewPipelineSubmit = async (data: {
    pipelineName: string;
    pipelineDescription: string;
    user_id: number;
  }) => {
    try {
      if (data.pipelineDescription && data.pipelineName) {
        // if we have both the description and the name then we create a new pipeline and refresh the page
        const token = await getCurrentToken();
        if (token) {
          const response = await createNewPipeline(
            token,
            data.pipelineName,
            data.pipelineDescription
          );
          if (response) {
            setListOfPipelines((prev) => [...prev, response]);
            showAlert("Successfully Created new Pipeline", "success");
          } else {
            showAlert("Failed to Create Pipeline", "error");
          }
        }
      }
    } catch (e) {
      console.log(e);
      showAlert("Error Creating Pipeline", "error");
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Error signing out", error);
    }
  };

  const deletePipelineHandler = async (data: { pipeline_id: number }) => {
    try {
      if (pipelineToDelete) {
        const token = await getCurrentToken();
        if (token) {
          const resultOfDeletion = await deletePipeline(
            token,
            data.pipeline_id
          );
          if (resultOfDeletion) {
            setListOfPipelines((prev) =>
              prev.filter((p) => p.pipeline_id !== data.pipeline_id)
            );
            showAlert("Successfully Deleted Pipeline", "success");
          } else {
            showAlert("Failed to Delete Pipeline", "error");
          }
        }
      }

      setPipelineToDelete(undefined);
      setOpenDeleteModal(false);
    } catch (e) {
      console.log(e);
      showAlert("Error Deleting Pipeline", "error");
    }
  };

  const goToSettingsHandler = async () => {};

  const handleDocumentUploadSuccess = () => {
    setRefreshDocuments((prev) => prev + 1);
    refreshPipelines();
  };

  const handleEditPipeline = async (data: {
    pipelineName: string;
    pipelineDescription: string;
    user_id: number;
  }) => {
    try {
      if (data.pipelineDescription && data.pipelineName) {
        const token = await getCurrentToken();
        if (token) {
          const response = await editPipeline(
            token,
            currentPipeline.pipeline_id,
            data.pipelineName,
            data.pipelineDescription
          );
          if (response) {
            setListOfPipelines((prev) =>
              prev.map((p) =>
                p.pipeline_id === response.pipeline_id ? response : p
              )
            );
            setCurrentPipeline(response);
            showAlert("Successfully Edited Pipeline", "success");
          } else {
            showAlert("Failed to Edit Pipeline", "error");
          }
        }
      }
    } catch (e) {
      console.log(e);
      showAlert("Error Editing Pipeline", "error");
    }
  };

  const retrievePipelineConversations = async (p: MySQLPipeline) => {
    try {
      const token = await getCurrentToken();
      if (token) {
        const response = await getConversations(token, p.pipeline_id);
        if (response) {
          setListOfConversations(response);
        }
      }
    } catch (e) {
      console.log(e);
      showAlert(
        "Error Retrieving Conversations for user and pipeline",
        "error"
      );
    }
  };

  const retrieveMessagesFromConvo = async (conversation_id: number) => {
    try {
      const token = await getCurrentToken();
      if (token) {
        const response = await getMessagesForConversation(
          token,
          conversation_id
        );
        if (response) {
          setCurrentMessages(response);
          console.log(response);
        }
      }
    } catch (e) {
      console.log(e);
      showAlert("Error Retrieving Messages from older conversation", "error");
    }
  };

  const conversationDeletionHandler = async () => {
    throw "Function not implemented yet";
  };

  const handleSendMessage = async (messageText: string) => {
    if (!currentConversation) return;
    console.log("Sending:", messageText);
    await retrieveMessagesFromConvo(currentConversation.conversation_id);
  };

  return (
    <div>
      <Box sx={{ display: "flex" }}>
        <CssBaseline />
        <AppBar
          position="fixed"
          open={open}
          sx={{
            backgroundColor: "#FFFFFF",
            color: "#212121",
            boxShadow: "0 1px 3px rgba(0,0,0,0.12)",
          }}
        >
          <Toolbar sx={{ justifyContent: "space-between", px: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                onClick={handleDrawerOpen}
                edge="start"
                sx={[
                  {
                    marginRight: 2,
                  },
                  open && { display: "none" },
                ]}
              >
                <MenuIcon />
              </IconButton>

              <Typography variant="h6" noWrap component="div">
                {viewMode ? "General Chat" : currentPipeline.pipeline_name}
              </Typography>
              {!viewMode ? (
                <IconButton
                  color="inherit"
                  aria-label="open drawer"
                  onClick={() => setOpenEditPipelineModal(true)}
                  edge="start"
                  sx={[
                    {
                      marginRight: 2,
                    },
                  ]}
                >
                  <EditSquareIcon />
                </IconButton>
              ) : null}
            </Box>

            <Box sx={{ display: "flex", alignItems: "center" }}>
              {!viewMode && (
                <>
                  <Box sx={{ mx: 2 }}>
                    <FilesButton
                      onClick={() => setShowChat(false)}
                      isActive={!showChat}
                    />
                  </Box>
                  <Box sx={{ mx: 2 }}>
                    <ChatButton
                      onClick={() => setShowChat(true)}
                      isActive={showChat}
                    />
                  </Box>
                  <Box sx={{ mx: 2 }}>
                    <FilesSearchBar />
                  </Box>
                  <Box sx={{ mx: 2 }}>
                    <UploadFilesButton
                      user={user}
                      pipeline={currentPipeline}
                      onUploadSuccess={handleDocumentUploadSuccess}
                    />
                  </Box>
                </>
              )}
            </Box>
            <Box>
              <Button
                variant="outlined"
                onClick={handleLogout}
                sx={{
                  textTransform: "none",
                  borderColor: "#212121",
                  color: "#212121",
                  "&:hover": {
                    borderColor: "#000000",
                    backgroundColor: "rgba(0, 0, 0, 0.04)",
                  },
                }}
              >
                {"Logout"}
              </Button>
            </Box>
          </Toolbar>
        </AppBar>
        <Drawer
          variant="permanent"
          open={open}
          sx={{
            "& .MuiDrawer-paper": {
              backgroundColor: "#F5F5F5",
              borderRight: "1px solid #E0E0E0",
            },
          }}
        >
          <DrawerHeader
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              px: 2,
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <img
                src="/src/assets/hoosStudyingBot.svg"
                alt="HoosStudying Logo"
                style={{
                  height: "2em",
                  width: "auto",
                  verticalAlign: "middle",
                }}
              />
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {"HoosStudying"}
              </Typography>
            </Box>

            <IconButton onClick={handleDrawerClose}>
              {theme.direction === "rtl" ? (
                <ChevronRightIcon />
              ) : (
                <ChevronLeftIcon />
              )}
            </IconButton>
          </DrawerHeader>

          <Divider />
          <List>
            <ListItem
              disablePadding
              sx={{
                minHeight: 48,
                px: 2.5,
                justifyContent: open ? "initial" : "center",
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  justifyContent: "center",
                  mr: open ? 3 : "auto",
                }}
              >
                <PersonIcon />
              </ListItemIcon>
              <ListItemText
                primary={`${user.first_name} ${user.last_name}`}
                secondary={user.email}
                sx={{
                  opacity: open ? 1 : 0,
                  "& .MuiListItemText-secondary": {
                    fontSize: "0.8rem",
                    color: "text.secondary",
                  },
                }}
              />
              {open && (
                <IconButton onClick={() => goToSettingsHandler()}>
                  <SettingsIcon />
                </IconButton>
              )}
            </ListItem>
            <Divider sx={{ mt: 1, mb: 1 }} />

            {!viewMode && (
              <div>
                <ListItem disablePadding sx={{ display: "block" }}>
                  <ListItemButton
                    sx={{
                      minHeight: 48,
                      px: 2.5,
                      justifyContent: open ? "initial" : "center",
                    }}
                    onClick={() => {
                      setViewMode(true);
                      setListOfConversations([]);
                      setCurrentConversation(undefined);
                      setCurrentMessages(undefined);
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: 0,
                        justifyContent: "center",
                        mr: open ? 3 : "auto",
                      }}
                    >
                      <ChatBubbleIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="General Chat"
                      sx={{ opacity: open ? 1 : 0 }}
                    />
                  </ListItemButton>
                </ListItem>
                <Divider sx={{ mt: 1, mb: 1 }} />
              </div>
            )}
          </List>
          {open && (
            <Typography
              variant="subtitle2"
              sx={{
                px: 2,
                pt: 2,
                pb: 1,
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                fontSize: "1.2rem",
              }}
            >
              {viewMode ? "Pipelines" : "Conversations"}
              {viewMode ? (
                <IconButton
                  aria-label="Create a new pipeline"
                  onClick={() => setOpenNewPipelineModal(true)}
                >
                  <AddIcon />
                </IconButton>
              ) : (
                <IconButton
                  aria-label="Go back to new conversation page"
                  onClick={() => setOpenGeneralPipelineChatPage(true)}
                >
                  <HomeIcon />
                </IconButton>
              )}
            </Typography>
          )}
          <List>
            {viewMode
              ? listOfPipelines.map((p, index) => (
                  <ListItem
                    key={p.pipeline_id}
                    disablePadding
                    sx={{ display: "block" }}
                  >
                    {open ? (
                      <ListItemButton
                        sx={{
                          minHeight: 48,
                          px: 2.5,
                          justifyContent: open ? "initial" : "center",
                        }}
                        onClick={() => {
                          setListOfConversations([]);
                          setCurrentConversation(undefined);
                          setCurrentMessages(undefined);
                          setOpenGeneralPipelineChatPage(true);
                          retrievePipelineConversations(p);
                          setViewMode(false);
                          setCurrentPipeline(p);
                        }}
                      >
                        <PipelineCard
                          pipeline_id={p.pipeline_id}
                          pipeline_name={p.pipeline_name}
                          pipeline_description={p.description}
                          number_of_documents={p.number_of_documents}
                          index={index}
                          onDelete={() => {
                            setOpenDeleteModal(true);
                            setPipelineToDelete(p);
                          }}
                        />
                      </ListItemButton>
                    ) : (
                      <ListItemButton
                        sx={{
                          minHeight: 48,
                          justifyContent: "center",
                        }}
                      >
                        {" "}
                        <ListItemIcon
                          sx={{ minWidth: 0, justifyContent: "center" }}
                        >
                          <Box
                            sx={{
                              position: "relative",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                            }}
                          >
                            <FolderIcon
                              sx={{ fontSize: 28, color: "#424242" }}
                            />
                            <Typography
                              sx={{
                                position: "absolute",
                                fontSize: "0.7rem",
                                fontWeight: 600,
                                color: "#FFFFFF",
                              }}
                            >
                              {index + 1}
                            </Typography>
                          </Box>
                        </ListItemIcon>
                      </ListItemButton>
                    )}
                  </ListItem>
                ))
              : listOfConversations.map((convo, index) => (
                  <ListItem
                    key={convo.conversation_id}
                    disablePadding
                    sx={{ display: "block" }}
                  >
                    {open ? (
                      <ListItemButton
                        sx={{
                          minHeight: 48,
                          px: 2.5,
                          justifyContent: open ? "initial" : "center",
                        }}
                        onClick={() => {
                          setViewMode(false);
                          setOpenGeneralPipelineChatPage(false);
                          setCurrentConversation(convo);
                          retrieveMessagesFromConvo(convo.conversation_id);
                        }}
                      >
                        <ConversationCard
                          conversation={convo}
                          index={index}
                          onDelete={conversationDeletionHandler}
                          isActive={
                            convo.conversation_id ==
                              currentConversation?.conversation_id &&
                            !openGeneralPipelineChatPage
                          }
                        />
                      </ListItemButton>
                    ) : (
                      <ListItemButton
                        sx={{
                          minHeight: 48,
                          justifyContent: "center",
                        }}
                      >
                        {" "}
                        <ListItemIcon
                          sx={{ minWidth: 0, justifyContent: "center" }}
                        >
                          <Box
                            sx={{
                              position: "relative",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                            }}
                          >
                            <FolderIcon
                              sx={{ fontSize: 28, color: "#424242" }}
                            />
                            <Typography
                              sx={{
                                position: "absolute",
                                fontSize: "0.7rem",
                                fontWeight: 600,
                                color: "#FFFFFF",
                              }}
                            >
                              {index + 1}
                            </Typography>
                          </Box>
                        </ListItemIcon>
                      </ListItemButton>
                    )}
                  </ListItem>
                ))}
          </List>
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1 }}>
          <DrawerHeader />
          {viewMode ? (
            <GeneralChatContainer user={user} isGeneral={true} />
          ) : !openGeneralPipelineChatPage && currentMessages && showChat ? (
            <ConversationView
              messages={currentMessages}
              user={user}
              onSendMessage={handleSendMessage}
            />
          ) : (
            <PipelineContainer
              user={user}
              pipeline={currentPipeline}
              showChat={showChat}
              refreshKey={refreshDocuments}
              onDocumentChange={refreshPipelines}
            />
          )}
        </Box>
      </Box>

      <CustomAlert
        message={alertState.message}
        open={alertState.open}
        severity={alertState.severity}
        onClose={() => setAlertState((prev) => ({ ...prev, open: false }))}
      />

      {openNewPipelineModal ? (
        <NewPipelineModal
          user_id={user.user_id}
          open={openNewPipelineModal}
          onClose={() => setOpenNewPipelineModal(false)}
          onSubmit={(data) => {
            handleNewPipelineSubmit(data);
            setOpenNewPipelineModal(false);
          }}
          isEditMode={false}
        />
      ) : null}

      {openDeleteModal && pipelineToDelete ? (
        <Dialog
          open={openDeleteModal}
          onClose={() => setOpenDeleteModal(false)}
          fullWidth
          maxWidth="sm"
        >
          <DialogTitle>
            {`Delete Pipeline ${pipelineToDelete.pipeline_name}`}
          </DialogTitle>
          <DialogContent>
            <Typography variant="body1" sx={{ mb: 2 }}>
              {
                "Are you sure you want to delete this pipeline? This action cannot be undone."
              }
            </Typography>
            <Typography variant="subtitle2" sx={{ color: "text.secondary" }}>
              {`Description: ${pipelineToDelete.description}`}
            </Typography>
            <Typography variant="subtitle2" sx={{ color: "text.secondary" }}>
              {`Files: ${pipelineToDelete.number_of_documents}`}
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDeleteModal(false)}>Cancel</Button>
            <Button
              variant="contained"
              color="error"
              onClick={() =>
                deletePipelineHandler({
                  pipeline_id: pipelineToDelete.pipeline_id,
                })
              }
            >
              {"Delete"}
            </Button>
          </DialogActions>
        </Dialog>
      ) : null}

      {openEditPipelineModal ? (
        <NewPipelineModal
          user_id={user.user_id}
          open={openEditPipelineModal}
          onClose={() => setOpenEditPipelineModal(false)}
          onSubmit={(data) => {
            handleEditPipeline(data);
            setOpenEditPipelineModal(false);
          }}
          isEditMode={true}
          pipeline={currentPipeline}
        />
      ) : null}
    </div>
  );
};

export default MainScreen;
