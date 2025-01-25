import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import { checkAdminStatus } from '../middleware/authGuard';
import Dashboard from "../views/Dashboard.vue";

const routes = [
    { path: "/", name: "Login", component: Login }, // Login page route
    { path: "/dashboard", name: "Dashboard", component: Dashboard },
    {
      path: '/signup',
      name: 'SignUp',
      component: () => import('../views/SignUp.vue')
    },
    {
      path: '/create-profile',
      name: 'CreateProfile',
      component: () => import('../views/CreateProfile.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('../views/Settings.vue')
    },
    {
      path: '/admin/users',
      name: 'UserManagement',
      component: () => import('../views/UserManagement.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true
      },
      beforeEnter: function(to, from, next) {
        const token = localStorage.getItem('token');
        if (!token) {
          next('/');
          return;
        }
  
        // Check if user is admin
        fetch(`${import.meta.env.VITE_API_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        .then(response => {
          if (!response.ok) throw new Error('Not authorized');
          return response.json();
        })
        .then(userData => {
          if (userData.is_superuser) {
            next();
          } else {
            next('/dashboard');
          }
        })
        .catch(() => {
          next('/dashboard');
        });
      }
    },
    {
      path: '/workouts',
      name: 'Workouts',
      component: () => import('../views/Workouts.vue')
    },
    {
      path: '/workout/:id',
      name: 'WorkoutId',
      component: () => import('../views/WorkoutId.vue')
    },
  ];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    next('/login');
  } else {
    next();
  }
});

export default router;
