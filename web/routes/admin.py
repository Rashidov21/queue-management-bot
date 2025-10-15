from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Optional

from database.simple_db import SessionLocal
from database.simple_db import User, Provider, Service, Booking, Slot
from simple_config import settings

router = APIRouter()


async def verify_admin(request: Request):
    """Simple admin verification"""
    if "admin_logged_in" not in request.session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return True


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard"""
    try:
        await verify_admin(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get dashboard statistics
    async with async_session_maker() as db:
        stats = await get_dashboard_stats(db)
        recent_activity = await get_recent_activity_html(db)
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Queue Bot Admin</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-gray-100">
        <nav class="bg-blue-600 text-white p-4">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">🤖 Queue Bot Admin</h1>
                <div>
                    <a href="/users" class="mx-2 hover:underline">👥 Users</a>
                    <a href="/services" class="mx-2 hover:underline">🔧 Services</a>
                    <a href="/bookings" class="mx-2 hover:underline">📅 Bookings</a>
                    <a href="/logout" class="mx-2 hover:underline">🚪 Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mx-auto p-6">
            <h2 class="text-3xl font-bold mb-6">📊 Dashboard</h2>
            
            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center">
                        <div class="p-2 bg-blue-100 rounded-lg">
                            <span class="text-2xl">👥</span>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Total Users</p>
                            <p class="text-2xl font-bold">{stats['total_users']}</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center">
                        <div class="p-2 bg-green-100 rounded-lg">
                            <span class="text-2xl">💼</span>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Active Providers</p>
                            <p class="text-2xl font-bold">{stats['active_providers']}</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center">
                        <div class="p-2 bg-yellow-100 rounded-lg">
                            <span class="text-2xl">📅</span>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Today's Bookings</p>
                            <p class="text-2xl font-bold">{stats['today_bookings']}</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center">
                        <div class="p-2 bg-purple-100 rounded-lg">
                            <span class="text-2xl">✅</span>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Total Bookings</p>
                            <p class="text-2xl font-bold">{stats['total_bookings']}</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Recent Activity -->
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-xl font-bold mb-4">📈 Recent Activity</h3>
                <div class="space-y-4">
                    {recent_activity}
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


@router.get("/login", response_class=HTMLResponse)
async def admin_login_page():
    """Admin login page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Login - Queue Bot</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 flex items-center justify-center min-h-screen">
        <div class="bg-white p-8 rounded-lg shadow-md w-96">
            <div class="text-center mb-6">
                <h1 class="text-3xl font-bold text-gray-800">🤖 Queue Bot</h1>
                <p class="text-gray-600">Admin Login</p>
            </div>
            
            <form method="post" action="/login">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
                        Username
                    </label>
                    <input class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500" 
                           type="text" id="username" name="username" required>
                </div>
                
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                        Password
                    </label>
                    <input class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500" 
                           type="password" id="password" name="password" required>
                </div>
                
                <button class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500" 
                        type="submit">
                    Login
                </button>
            </form>
        </div>
    </body>
    </html>
    """)


@router.post("/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Process admin login"""
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        request.session["admin_logged_in"] = True
        return RedirectResponse(url="/", status_code=302)
    else:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login Failed</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 flex items-center justify-center min-h-screen">
            <div class="bg-white p-8 rounded-lg shadow-md w-96 text-center">
                <div class="text-red-500 text-6xl mb-4">❌</div>
                <h2 class="text-2xl font-bold text-gray-800 mb-4">Login Failed</h2>
                <p class="text-gray-600 mb-6">Invalid username or password.</p>
                <a href="/login" class="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">
                    Try Again
                </a>
            </div>
        </body>
        </html>
        """, status_code=401)


@router.get("/logout")
async def admin_logout(request: Request):
    """Admin logout"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    """Users management page"""
    try:
        await verify_admin(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get users
    async with async_session_maker() as db:
        result = await db.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
    
    users_html = ""
    for user in users:
        role_emoji = "💼" if user.role == "provider" else "👤"
        users_html += f"""
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">{role_emoji}</td>
            <td class="px-6 py-4 whitespace-nowrap">{user.full_name}</td>
            <td class="px-6 py-4 whitespace-nowrap">{user.role.title()}</td>
            <td class="px-6 py-4 whitespace-nowrap">{user.phone or 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap">{user.created_at.strftime('%Y-%m-%d')}</td>
        </tr>
        """
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Users - Queue Bot Admin</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <nav class="bg-blue-600 text-white p-4">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">🤖 Queue Bot Admin</h1>
                <div>
                    <a href="/admin" class="mx-2 hover:underline">📊 Dashboard</a>
                    <a href="/users" class="mx-2 hover:underline">👥 Users</a>
                    <a href="/services" class="mx-2 hover:underline">🔧 Services</a>
                    <a href="/bookings" class="mx-2 hover:underline">📅 Bookings</a>
                    <a href="/logout" class="mx-2 hover:underline">🚪 Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mx-auto p-6">
            <h2 class="text-3xl font-bold mb-6">👥 Users</h2>
            
            <div class="bg-white rounded-lg shadow overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {users_html}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """)


@router.get("/services", response_class=HTMLResponse)
async def admin_services(request: Request):
    """Services management page"""
    try:
        await verify_admin(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get services
    async with async_session_maker() as db:
        result = await db.execute(select(Service).order_by(Service.name))
        services = result.scalars().all()
        
        services_html = ""
        for service in services:
            # Count providers for this service
            provider_count_result = await db.execute(
                select(func.count(Provider.id)).where(Provider.service_id == service.id)
            )
            provider_count = provider_count_result.scalar()
        
        services_html += f"""
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">🔧</td>
            <td class="px-6 py-4 whitespace-nowrap font-medium">{service.name}</td>
            <td class="px-6 py-4">{service.description or 'No description'}</td>
            <td class="px-6 py-4 whitespace-nowrap">{provider_count}</td>
            <td class="px-6 py-4 whitespace-nowrap">{service.created_at.strftime('%Y-%m-%d')}</td>
        </tr>
        """
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Services - Queue Bot Admin</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <nav class="bg-blue-600 text-white p-4">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">🤖 Queue Bot Admin</h1>
                <div>
                    <a href="/admin" class="mx-2 hover:underline">📊 Dashboard</a>
                    <a href="/users" class="mx-2 hover:underline">👥 Users</a>
                    <a href="/services" class="mx-2 hover:underline">🔧 Services</a>
                    <a href="/bookings" class="mx-2 hover:underline">📅 Bookings</a>
                    <a href="/logout" class="mx-2 hover:underline">🚪 Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mx-auto p-6">
            <h2 class="text-3xl font-bold mb-6">🔧 Services</h2>
            
            <div class="bg-white rounded-lg shadow overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Icon</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Providers</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {services_html}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """)


@router.get("/bookings", response_class=HTMLResponse)
async def admin_bookings(request: Request):
    """Bookings management page"""
    try:
        await verify_admin(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get bookings
    async with async_session_maker() as db:
        result = await db.execute(
            select(Booking, Slot, Provider, User, Service)
            .join(Slot, Booking.slot_id == Slot.id)
            .join(Provider, Slot.provider_id == Provider.id)
            .join(User, Booking.client_id == User.id)
            .join(Service, Provider.service_id == Service.id)
            .order_by(Slot.date.desc(), Slot.time.desc())
        )
        bookings = result.all()
    
    bookings_html = ""
    for booking, slot, provider, client, service in bookings:
        status_emoji = "✅" if booking.status == "active" else "❌" if booking.status == "cancelled" else "✅"
        bookings_html += f"""
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">{status_emoji}</td>
            <td class="px-6 py-4 whitespace-nowrap">{client.full_name}</td>
            <td class="px-6 py-4 whitespace-nowrap">{provider.user.full_name}</td>
            <td class="px-6 py-4 whitespace-nowrap">{service.name}</td>
            <td class="px-6 py-4 whitespace-nowrap">{slot.date}</td>
            <td class="px-6 py-4 whitespace-nowrap">{slot.time}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs rounded-full {'bg-green-100 text-green-800' if booking.status == 'active' else 'bg-red-100 text-red-800'}">
                    {booking.status.title()}
                </span>
            </td>
        </tr>
        """
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bookings - Queue Bot Admin</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <nav class="bg-blue-600 text-white p-4">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">🤖 Queue Bot Admin</h1>
                <div>
                    <a href="/admin" class="mx-2 hover:underline">📊 Dashboard</a>
                    <a href="/users" class="mx-2 hover:underline">👥 Users</a>
                    <a href="/services" class="mx-2 hover:underline">🔧 Services</a>
                    <a href="/bookings" class="mx-2 hover:underline">📅 Bookings</a>
                    <a href="/logout" class="mx-2 hover:underline">🚪 Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mx-auto p-6">
            <h2 class="text-3xl font-bold mb-6">📅 Bookings</h2>
            
            <div class="bg-white rounded-lg shadow overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Client</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Service</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Booking Status</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {bookings_html}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """)


async def get_dashboard_stats(db: AsyncSession):
    """Get dashboard statistics"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Total users
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    # Active providers
    active_providers_result = await db.execute(
        select(func.count(Provider.id)).where(Provider.is_accepting == True)
    )
    active_providers = active_providers_result.scalar()
    
    # Today's bookings
    today_bookings_result = await db.execute(
        select(func.count(Booking.id))
        .join(Slot, Booking.slot_id == Slot.id)
        .where(and_(Slot.date == today, Booking.status == "active"))
    )
    today_bookings = today_bookings_result.scalar()
    
    # Total bookings
    total_bookings_result = await db.execute(select(func.count(Booking.id)))
    total_bookings = total_bookings_result.scalar()
    
    return {
        "total_users": total_users,
        "active_providers": active_providers,
        "today_bookings": today_bookings,
        "total_bookings": total_bookings
    }


async def get_recent_activity_html(db: AsyncSession):
    """Get recent activity HTML"""
    # Get recent bookings
    result = await db.execute(
        select(Booking, Slot, Provider, User, Service)
        .join(Slot, Booking.slot_id == Slot.id)
        .join(Provider, Slot.provider_id == Provider.id)
        .join(User, Booking.client_id == User.id)
        .join(Service, Provider.service_id == Service.id)
        .order_by(Booking.created_at.desc())
        .limit(5)
    )
    recent_bookings = result.all()
    
    activity_html = ""
    for booking, slot, provider, client, service in recent_bookings:
        status_emoji = "✅" if booking.status == "active" else "❌"
        activity_html += f"""
        <div class="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
            <div class="text-2xl">{status_emoji}</div>
            <div class="flex-1">
                <p class="font-medium">{client.full_name} booked {service.name}</p>
                <p class="text-sm text-gray-600">with {provider.user.full_name} on {slot.date} at {slot.time}</p>
            </div>
            <div class="text-sm text-gray-500">
                {booking.created_at.strftime('%m/%d %H:%M')}
            </div>
        </div>
        """
    
    return activity_html
