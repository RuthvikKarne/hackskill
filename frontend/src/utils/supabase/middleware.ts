import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '',
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => request.cookies.set(name, value));
          supabaseResponse = NextResponse.next({
            request,
          });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const isHospitalRoute = request.nextUrl.pathname.startsWith("/dashboard");
  const isVendorRoute = request.nextUrl.pathname.startsWith("/vendor");
  const isLoginRoute = request.nextUrl.pathname === "/";

  // Check if they are trying to access protected routes
  if (isHospitalRoute || isVendorRoute) {
    if (!user) {
      // Unauthenticated users are redirected to login
      const url = request.nextUrl.clone();
      url.pathname = "/";
      return NextResponse.redirect(url);
    }

    // Role-based routing
    const role = user.user_metadata?.role || "hospital"; // default to hospital if no role

    if (role === "vendor" && isHospitalRoute) {
      // Vendors cannot access hospital dashboard
      const url = request.nextUrl.clone();
      url.pathname = "/vendor";
      return NextResponse.redirect(url);
    }

    if (role === "hospital" && isVendorRoute) {
      // Hospitals cannot access vendor dashboard
      const url = request.nextUrl.clone();
      url.pathname = "/dashboard";
      return NextResponse.redirect(url);
    }
  }

  // Redirect authenticated users away from the login page
  if (isLoginRoute && user) {
    const role = user.user_metadata?.role || "hospital";
    const url = request.nextUrl.clone();
    url.pathname = role === "vendor" ? "/vendor" : "/dashboard";
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}
