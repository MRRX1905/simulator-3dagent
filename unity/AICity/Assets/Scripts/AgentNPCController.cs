using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

namespace AICity
{
    [Serializable]
    public class AgentData
    {
        public string id;
        public string name;
        public string role;
        public string status;
        public string location;
        public float money;
        public int reputation;
    }

    /// <summary>
    /// Controls 3D Humanoid Agent NPCs in Unity, moving between workplaces and homes.
    /// </summary>
    public class AgentNPCController : MonoBehaviour
    {
        [Header("Prefabs")]
        public GameObject npcPrefab;

        [Header("Waypoints")]
        public Transform cityHallWaypoint;
        public Transform techHubWaypoint;
        public Transform qaLabWaypoint;
        public Transform academyWaypoint;
        public Transform residentialWaypoint;

        private Dictionary<string, GameObject> spawnedAgents = new Dictionary<string, GameObject>();

        public void UpdateAgentsFromBackend(string jsonArray)
        {
            // Parses agent array and updates NavMesh destinations and animations
            // e.g. If status == "EXECUTING" and role == "developer", agent walks to Tech Hub.
        }

        public void MoveAgentTo(string agentId, Vector3 destination)
        {
            if (spawnedAgents.ContainsKey(agentId))
            {
                NavMeshAgent nav = spawnedAgents[agentId].GetComponent<NavMeshAgent>();
                if (nav != null)
                {
                    nav.SetDestination(destination);
                }
            }
        }
    }
}
