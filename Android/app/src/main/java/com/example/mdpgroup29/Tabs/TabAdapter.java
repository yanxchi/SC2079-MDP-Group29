package com.example.mdpgroup29.Tabs;
import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentActivity;
import androidx.viewpager2.adapter.FragmentStateAdapter;

public class TabAdapter extends FragmentStateAdapter {

    public TabAdapter(@NonNull FragmentActivity fragmentActivity) {
        super(fragmentActivity);
    }

    @NonNull
    @Override
    public Fragment createFragment(int position) {
        switch (position) {
            case 0:
                return new ArenaFragment(); // Arena Fragment
            case 1:
                return new ControllerFragment(); // Controller Fragment
            case 2:
                return new ChatFragment(); // Chat Fragment
            default:
                return new ArenaFragment(); // Show Arena controls by default
        }
    }

    @Override
    public int getItemCount() {
        return 3; // Abstract class method that is required to be implemented
    }
}