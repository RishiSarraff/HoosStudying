import React, { useEffect, useState } from "react";
import { Typography, Box, ThemeProvider } from "@mui/material";
import AuthPage from "./components/AuthPage";
import { setupAuthListener, getCurrentToken } from "./services/auth";
import type { MySQLPipeline, MySQLUser } from "./types";
import axios from "axios";
import NameModal from "./components/NameModal";
import MainScreen from "./components/MainScreen";
import {
  getDefaultUserPipeline,
  getAllNonDefaultPipelines,
} from "./services/pipeline";
import theme from "./theme";

const App: React.FC = () => {
  const [user, setUser] = useState<MySQLUser | null>(null);
  const [pipeline, setPipeline] = useState<MySQLPipeline | null>(null);
  const [needsName, setNeedsName] = useState(false);
  const [loading, setLoading] = useState(true);
  const [listOfPipelines, setListOfPipelines] = useState<MySQLPipeline[]>([]);

  const fetchDefaultPipeline = async (token: string) => {
    try {
      const defaultPipeline = await getDefaultUserPipeline(token);
      setPipeline(defaultPipeline);
    } catch (err) {
      console.error("Failed to fetch default pipeline", err);
    }
  };
  const fetchNonDefaultPipelines = async (token: string) => {
    try {
      const nonDefaultPipelines = await getAllNonDefaultPipelines(token);
      setListOfPipelines(nonDefaultPipelines);
    } catch (err) {
      console.error("Failed to fetch all non default pipelines", err);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      console.warn("Auth listener timeout - setting loading to false");
      setLoading(false);
    }, 10000);

    const unsubscribe = setupAuthListener(
      async (mysqlUser) => {
        try {
          clearTimeout(timeoutId);
          setUser(mysqlUser);
          if (mysqlUser.needs_name) {
            setNeedsName(true);
          } else {
            const token = await getCurrentToken();
            if (token) {
              await fetchDefaultPipeline(token);
              await fetchNonDefaultPipelines(token);
            }
          }
        } catch (error) {
          console.error("Error in auth callback:", error);
        } finally {
          clearTimeout(timeoutId);
          setLoading(false);
        }
      },
      () => {
        clearTimeout(timeoutId);
        setUser(null);
        setPipeline(null);
        setListOfPipelines([]);
        setLoading(false);
      }
    );

    return () => {
      clearTimeout(timeoutId);
      unsubscribe();
    };
  }, []);

  if (loading) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Typography variant="h4">Loading...</Typography>
      </Box>
    );
  }

  if (!user) {
    return <AuthPage />;
  }

  return (
    <ThemeProvider theme={theme}>
      <div>
        {needsName && (
          <NameModal
            onSubmit={async (first_name, last_name) => {
              const token = await getCurrentToken();

              await axios.post(
                "http://localhost:8000/api/auth/user/update-name",
                { first_name, last_name },
                { headers: { Authorization: `Bearer ${token}` } }
              );

              if (user) {
                setUser({ ...user, first_name, last_name, needs_name: false });
              }

              setNeedsName(false);
            }}
          />
        )}
        {user && pipeline ? (
          <div>
            <MainScreen
              key={user.user_id}
              user={user}
              pipeline={pipeline}
              listOfPipelines={listOfPipelines}
            />
          </div>
        ) : (
          <div></div>
        )}
      </div>
    </ThemeProvider>
  );
};

export default App;
